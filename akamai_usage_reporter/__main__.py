import argparse
import csv
import json
import os
import sys
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import requests
from requests.auth import AuthBase
from akamai.edgegrid import EdgeGridAuth  # from edgegrid-python
import tldextract


def auto_load_environment():
    """Automatically load virtual environment and .env file if needed."""
    # Check if we're in a virtual environment
    if not hasattr(sys, "real_prefix") and not (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        # Not in a virtual environment, try to activate it
        venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".venv")
        if os.path.exists(venv_path):
            print("Auto-activating virtual environment...", file=sys.stderr)
            # Add venv site-packages to Python path
            site_packages = os.path.join(venv_path, "lib", "python3.9", "site-packages")
            if os.path.exists(site_packages):
                sys.path.insert(0, site_packages)
                print(f"Added {site_packages} to Python path", file=sys.stderr)

    # Load environment variables from akamai.env file
    env_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "akamai.env")
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}", file=sys.stderr)
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded: {key}", file=sys.stderr)
    else:
        print(f"Environment file not found: {env_file}", file=sys.stderr)
        print("Please create akamai.env with your Akamai credentials", file=sys.stderr)


# Auto-load environment when module is imported
auto_load_environment()


DEFAULT_TIMEOUT = (10, 60)


class EdgegridAuthEnv(AuthBase):
    """Auth that prefers env vars over edgerc, compatible with requests."""

    def __init__(
        self, host: str, client_token: str, client_secret: str, access_token: str
    ):
        self.session = requests.Session()
        self.session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
        )
        self.host = host.rstrip("/")

    def __call__(self, r):
        # Delegate signing to EdgeGridAuth set on a temp session
        return self.session.auth(r)


@dataclass
class ApiContext:
    base_url: str
    auth: AuthBase
    account_switch_key: Optional[str] = None

    def build_url(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        params = dict(params or {})
        if self.account_switch_key:
            params["accountSwitchKey"] = self.account_switch_key
        return url, params

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url, params = self.build_url(path, params)
        resp = requests.get(url, auth=self.auth, params=params, timeout=DEFAULT_TIMEOUT)
        resp.raise_for_status()
        return resp.json()


# ---------------- PAPI helpers -----------------


def papi_list_properties(api: ApiContext) -> List[Dict[str, Any]]:
    try:
        print("Fetching properties from PAPI...", file=sys.stderr)

        # First, try to get contracts and groups to find valid IDs
        print("Getting contracts and groups...", file=sys.stderr)
        contracts_data = api.get("papi/v1/contracts")
        contracts = contracts_data.get("contracts", {}).get("items", [])

        if not contracts:
            print("No contracts found", file=sys.stderr)
            return []

        # Find the best working contract-group combination
        print("Finding working contract-group combination...", file=sys.stderr)

        # Get all groups to find valid combinations
        groups_data = api.get("papi/v1/groups")
        groups = groups_data.get("groups", {}).get("items", [])

        if not groups:
            print("No groups found", file=sys.stderr)
            return []

        # Find a working combination (prioritize ones with properties)
        working_combination = None

        for contract in contracts:
            contract_id = contract.get("contractId")

            for group in groups:
                group_id = group.get("groupId")
                group_contracts = group.get("contractIds", [])

                # Check if this group can be used with this contract
                if contract_id in group_contracts:
                    print(
                        f"Testing contract {contract_id} with group {group_id}...",
                        file=sys.stderr,
                    )

                    try:
                        # Test if this combination works
                        test_data = api.get(
                            "papi/v1/properties",
                            params={"contractId": contract_id, "groupId": group_id},
                        )

                        properties = test_data.get("properties", {}).get("items", [])
                        if properties:
                            working_combination = {
                                "contractId": contract_id,
                                "groupId": group_id,
                                "propertiesCount": len(properties),
                            }
                            print(
                                f"✓ Found working combination: {contract_id} + {group_id} ({len(properties)} properties)",
                                file=sys.stderr,
                            )
                            break
                    except Exception:
                        continue

            if working_combination:
                break

        if not working_combination:
            print("No working contract-group combinations found", file=sys.stderr)
            return []

        contract_id = working_combination["contractId"]
        group_id = working_combination["groupId"]

        print(f"Using contract: {contract_id} with group: {group_id}", file=sys.stderr)

        # Now call properties with required parameters
        data = api.get(
            "papi/v1/properties",
            params={"contractId": contract_id, "groupId": group_id},
        )

        properties = data.get("properties", {}).get("items", [])
        print(f"Found {len(properties)} properties", file=sys.stderr)
        return properties
    except Exception as e:
        print(f"Error fetching properties: {e}", file=sys.stderr)
        if hasattr(e, "response") and hasattr(e.response, "status_code"):
            print(f"HTTP Status: {e.response.status_code}", file=sys.stderr)
            print(f"Response: {e.response.text}", file=sys.stderr)
        raise


def papi_list_property_versions(
    api: ApiContext, property_id: str
) -> List[Dict[str, Any]]:
    data = api.get(f"papi/v1/properties/{property_id}/versions")
    return data.get("versions", {}).get("items", [])


def papi_get_hostnames(
    api: ApiContext, property_id: str, version: int, contract_id: str, group_id: str
) -> List[Dict[str, Any]]:
    data = api.get(
        f"papi/v1/properties/{property_id}/versions/{version}/hostnames",
        params={"contractId": contract_id, "groupId": group_id},
    )
    return data.get("hostnames", {}).get("items", [])


def papi_get_rules(
    api: ApiContext, property_id: str, version: int, contract_id: str, group_id: str
) -> Dict[str, Any]:
    data = api.get(
        f"papi/v1/properties/{property_id}/versions/{version}/rules",
        params={"contractId": contract_id, "groupId": group_id},
    )
    return data.get("rules", {})


# ---------------- CPS helpers -----------------


def cps_list_enrollments(api: ApiContext) -> List[Dict[str, Any]]:
    try:
        data = api.get("cps/v2/enrollments")
        return data.get("enrollments", [])
    except Exception:
        return []


# ---------------- AppSec helpers -----------------


def appsec_list_configs(api: ApiContext) -> List[Dict[str, Any]]:
    try:
        data = api.get("appsec/v1/configs")
        return data.get("configs", [])
    except Exception:
        return []


def appsec_list_policies(
    api: ApiContext, config_id: int, version: int
) -> List[Dict[str, Any]]:
    try:
        data = api.get(
            f"appsec/v1/configs/{config_id}/versions/{version}/security-policies"
        )
        return data.get("policies", [])
    except Exception:
        return []


# ---------------- rules parsing -----------------


def flatten_rules(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    nodes: List[Dict[str, Any]] = []
    stack = [node]
    while stack:
        current = stack.pop()
        nodes.append(current)
        for child in current.get("children", []) or []:
            stack.append(child)
    return nodes


def parse_behaviors(rules_root: Dict[str, Any]) -> Dict[str, Any]:
    parsed: Dict[str, Any] = {
        "cache": [],
        "redirects": [],
        "headers": [],
        "hsts": [],
    }
    for node in flatten_rules(rules_root):
        for behavior in node.get("behaviors", []) or []:
            name = behavior.get("name")
            options = behavior.get("options", {})
            if name == "caching":
                parsed["cache"].append(options)
            elif name in ("redirect", "responseCode") and options:
                parsed["redirects"].append(options)
            elif name in (
                "modifyOutgoingResponseHeader",
                "modifyOutgoingRequestHeader",
            ):
                parsed["headers"].append({"name": name, **options})
            elif (
                name == "hsts"
                or name == "httpStrictTransportSecurity"
                or name == "setHsts"
                or name == "setResponseHeader"
                and options.get("headerName", "").lower() == "strict-transport-security"
            ):
                parsed["hsts"].append(options)
    return parsed


# ---------------- reporting -----------------


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def apex_of(hostname: str) -> str:
    t = tldextract.extract(hostname)
    if not t.registered_domain:
        return hostname
    return t.registered_domain


# ---------------- Additional product helpers -----------------


def edgedns_list_zones(api: ApiContext) -> List[Dict[str, Any]]:
    """Edge DNS zones via Config DNS API. Try v2 then v1 for compatibility."""
    try:
        data = api.get("config-dns/v2/zones")
        zones = data.get("zones", [])
        if zones:
            return zones
    except Exception:
        pass
    try:
        data = api.get("config-dns/v1/zones")
        return data.get("zones", [])
    except Exception:
        return []


def gtm_list_domains(api: ApiContext) -> List[str]:
    try:
        data = api.get("gtm/v1/domains")
        # Some accounts return { "items": ["domain"] }, others simple list
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_list_datacenters(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/datacenters")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_list_properties(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/properties")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_get_property(
    api: ApiContext, domain: str, property_name: str
) -> Dict[str, Any]:
    try:
        return api.get(f"gtm/v1/domains/{domain}/properties/{property_name}")
    except Exception:
        return {}


def gtm_list_liveness_tests(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/liveness-tests")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_list_cidr_maps(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/cidr-maps")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_list_geo_maps(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/geo-maps")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def gtm_list_as_maps(api: ApiContext, domain: str) -> List[Dict[str, Any]]:
    try:
        data = api.get(f"gtm/v1/domains/{domain}/as-maps")
        if isinstance(data, dict) and "items" in data:
            return data.get("items", [])
        if isinstance(data, list):
            return data
        return []
    except Exception:
        return []


def edgeworkers_list(api: ApiContext) -> List[Dict[str, Any]]:
    try:
        data = api.get("edgeworkers/v1/edgeworkers")
        return data.get("edgeworkers", [])
    except Exception:
        return []


def cloudlets_list_policies(api: ApiContext) -> List[Dict[str, Any]]:
    try:
        data = api.get("cloudlets/v2/policies")
        return data.get("policies", []) if isinstance(data, dict) else data
    except Exception:
        return []


def cloud_wrapper_list(api: ApiContext) -> List[Dict[str, Any]]:
    """Attempt to enumerate Cloud Wrapper containers/configs using known endpoints."""
    for path in ("cloud-wrapper/v1/containers", "cloud-wrapper/v1/configurations"):
        try:
            data = api.get(path)
            # Return first non-empty list-like response
            if isinstance(data, dict):
                items = (
                    data.get("items")
                    or data.get("containers")
                    or data.get("configurations")
                    or []
                )
                if items:
                    return items
            if isinstance(data, list) and data:
                return data
        except Exception:
            continue
    return []


@dataclass
class HostnameRecord:
    apex: str
    hostname: str
    property_name: str
    property_id: str
    property_version: int


def write_csv(path: str, headers: List[str], rows: List[List[Any]]) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def write_text(path: str, content: str) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def write_json(path: str, obj: Any) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


def generate_checklist(
    apex: str,
    host_records: List[HostnameRecord],
    parsed_by_property: Dict[str, Dict[str, Any]],
    cps_by_sni: Dict[str, List[str]],
) -> str:
    lines: List[str] = []
    lines.append(f"# Cloudflare migration checklist for {apex}")
    lines.append("")
    lines.append("- Create zone in Cloudflare")
    lines.append("- Set DNS nameservers or use partial (CNAME) setup as applicable")
    lines.append("- Enable Universal SSL or upload cert matching SANs")
    if apex in cps_by_sni:
        lines.append(f"  - CPS SANs: {', '.join(sorted(set(cps_by_sni[apex])))}")
    lines.append("- Enable WAF managed rules; recreate custom WAF rules")
    lines.append("- Recreate cache rules and overrides")
    lines.append("- Recreate redirects (Transform or Rulesets)")
    lines.append("- Recreate header rules; enable HSTS if present")
    lines.append("")
    lines.append("## Hostnames")
    for hr in sorted(host_records, key=lambda r: r.hostname):
        lines.append(
            f"- {hr.hostname} (property {hr.property_name} v{hr.property_version})"
        )
    lines.append("")
    lines.append("## Rules summary")
    for hr in sorted(host_records, key=lambda r: (r.property_name, r.property_version)):
        key = f"{hr.property_id}:{hr.property_version}"
        parsed = parsed_by_property.get(key)
        if not parsed:
            continue
        lines.append(f"### {hr.property_name} v{hr.property_version}")
        if parsed.get("cache"):
            lines.append("- Cache behaviors present")
        if parsed.get("redirects"):
            lines.append("- Redirect rules present")
        if parsed.get("headers"):
            lines.append("- Header modifications present")
        if parsed.get("hsts"):
            lines.append("- HSTS present")
        lines.append("")
    return "\n".join(lines)


# ---------------- main CLI -----------------


def env_or_none(name: str) -> Optional[str]:
    val = os.environ.get(name)
    return val if val else None


def build_api_context(
    section: Optional[str], account_switch_key: Optional[str]
) -> ApiContext:
    host = env_or_none("AKAMAI_HOST")
    client_token = env_or_none("AKAMAI_CLIENT_TOKEN")
    client_secret = env_or_none("AKAMAI_CLIENT_SECRET")
    access_token = env_or_none("AKAMAI_ACCESS_TOKEN")

    if not all([host, client_token, client_secret, access_token]):
        print("Missing EdgeGrid env vars. Please set:", file=sys.stderr)
        print("  AKAMAI_HOST", file=sys.stderr)
        print("  AKAMAI_CLIENT_TOKEN", file=sys.stderr)
        print("  AKAMAI_CLIENT_SECRET", file=sys.stderr)
        print("  AKAMAI_ACCESS_TOKEN", file=sys.stderr)
        sys.exit(2)

    # Validate host format
    if not host.startswith(("akab-", "akamai")):
        print(
            f"Warning: AKAMAI_HOST '{host}' doesn't look like a standard Akamai hostname",
            file=sys.stderr,
        )

    print(f"Connecting to Akamai host: {host}", file=sys.stderr)
    if account_switch_key:
        print(f"Using account switch key: {account_switch_key[:8]}...", file=sys.stderr)

    auth = EdgegridAuthEnv(host, client_token, client_secret, access_token)
    base = f"https://{host}"
    return ApiContext(base_url=base, auth=auth, account_switch_key=account_switch_key)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Akamai usage reporter → Cloudflare checklist"
    )
    parser.add_argument(
        "--out-dir", default="./out", help="Output directory for reports"
    )
    parser.add_argument(
        "--include-rules",
        action="store_true",
        help="Fetch and parse rules for caching/redirects/headers/HSTS",
    )
    parser.add_argument(
        "--edgerc-section",
        default=None,
        help="Unused for now; placeholder if edgerc support is added",
    )
    parser.add_argument(
        "--account-switch-key", default=env_or_none("AKAMAI_ACCOUNT_SWITCH_KEY")
    )
    parser.add_argument(
        "--include-products",
        action="store_true",
        help="Enumerate Edge DNS zones, GTM, EdgeWorkers, Cloudlets, Cloud Wrapper",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output and detailed error information",
    )

    args = parser.parse_args(argv)

    if args.debug:
        print("=== Debug Mode Enabled ===", file=sys.stderr)
        print(f"Output directory: {args.out_dir}", file=sys.stderr)
        print(f"Include rules: {args.include_rules}", file=sys.stderr)
        print(f"Include products: {args.include_products}", file=sys.stderr)
        print(
            f"Account switch key: {args.account_switch_key[:8] if args.account_switch_key else 'None'}...",
            file=sys.stderr,
        )

    api = build_api_context(args.edgerc_section, args.account_switch_key)

    try:
        properties = papi_list_properties(api)
    except Exception as e:
        print(f"Failed to fetch properties: {e}", file=sys.stderr)
        if args.debug:
            print("Full error details:", file=sys.stderr)
            import traceback

            traceback.print_exc()
        sys.exit(1)

    host_records: List[HostnameRecord] = []
    parsed_by_property: Dict[str, Dict[str, Any]] = {}

    for prop in properties:
        property_id = prop.get("propertyId")
        property_name = prop.get("propertyName")
        latest_version = (
            prop.get("latestVersion")
            or prop.get("productionVersion")
            or prop.get("stagingVersion")
        )
        if not property_id or not latest_version:
            continue
        contract_id = prop.get("contractId")
        group_id = prop.get("groupId")
        try:
            hostnames = papi_get_hostnames(
                api, property_id, int(latest_version), contract_id, group_id
            )
        except Exception:
            hostnames = []
        for hn in hostnames:
            cert_status = hn.get("certStatus") or hn.get("edgeHostnameId") or ""
            host_records.append(
                HostnameRecord(
                    apex=apex_of(hn.get("cnameFrom") or hn.get("hostname", "")),
                    hostname=hn.get("cnameFrom") or hn.get("hostname", ""),
                    property_name=property_name,
                    property_id=property_id,
                    property_version=int(latest_version),
                )
            )
        if args.include_rules:
            try:
                rules = papi_get_rules(
                    api, property_id, int(latest_version), contract_id, group_id
                )
                parsed_by_property[f"{property_id}:{latest_version}"] = parse_behaviors(
                    rules
                )
            except Exception:
                pass

    # CPS
    cps = cps_list_enrollments(api)
    cps_by_sni: Dict[str, List[str]] = defaultdict(list)
    cps_rows: List[List[Any]] = []
    for enr in cps:
        sans = (
            enr.get("csr", {}).get("sans", [])
            or enr.get("networkConfiguration", {}).get("sanEntries", [])
            or []
        )
        common_name = enr.get("csr", {}).get("cn") or enr.get("certificate", {}).get(
            "cn"
        )
        names = [common_name] if common_name else []
        names.extend(sans)
        for name in names:
            if not name:
                continue
            cps_by_sni[apex_of(name)].append(name)
        cps_rows.append(
            [
                enr.get("id"),
                common_name or "",
                ";".join(sans),
                enr.get("status"),
                enr.get("deploymentSchedule", {}).get("network", ""),
            ]
        )

    # AppSec high-level
    appsec_configs = appsec_list_configs(api)
    appsec_rows: List[List[Any]] = []
    for cfg in appsec_configs:
        latest = cfg.get("latestVersion", {}).get("version") or cfg.get("latestVersion")
        config_id = cfg.get("id") or cfg.get("configId")
        config_name = cfg.get("name") or cfg.get("configName")
        policies = (
            appsec_list_policies(api, int(config_id), int(latest))
            if (config_id and latest)
            else []
        )
        appsec_rows.append([config_id, config_name, latest, len(policies)])

    # Optional additional products
    products_rows: Dict[str, List[List[Any]]] = {}
    if args.include_products:
        zones = edgedns_list_zones(api)
        products_rows["edgedns_zones.csv"] = [
            [
                z.get("zone") or z.get("name"),
                z.get("type") or z.get("contractId"),
                z.get("status") or "",
            ]
            for z in zones
        ]

        gtm_domains = gtm_list_domains(api)
        products_rows["gtm_domains.csv"] = [[d] for d in gtm_domains]

        ews = edgeworkers_list(api)
        products_rows["edgeworkers.csv"] = [
            [
                ew.get("edgeWorkerId"),
                ew.get("name"),
                ew.get("groupId"),
                ew.get("lastModifiedTime"),
            ]
            for ew in ews
        ]

        cloudlets = cloudlets_list_policies(api)
        products_rows["cloudlets_policies.csv"] = [
            [
                cl.get("policyId"),
                cl.get("name"),
                cl.get("cloudletType"),
                cl.get("status"),
            ]
            for cl in cloudlets
        ]

        cw = cloud_wrapper_list(api)
        products_rows["cloud_wrapper.csv"] = [
            [
                c.get("id") or c.get("containerId"),
                c.get("name"),
                c.get("status") or c.get("state"),
            ]
            for c in cw
        ]

    # Write CSVs
    out_dir = args.out_dir
    usage_rows: List[List[Any]] = []
    for hr in host_records:
        usage_rows.append(
            [
                hr.apex,
                hr.hostname,
                hr.property_name,
                hr.property_id,
                hr.property_version,
            ]
        )
    write_csv(
        os.path.join(out_dir, "usage_summary.csv"),
        ["apex", "hostname", "property_name", "property_id", "property_version"],
        usage_rows,
    )

    write_csv(
        os.path.join(out_dir, "hostnames.csv"),
        ["hostname", "apex", "property_name", "property_id", "property_version"],
        [
            [
                hr.hostname,
                hr.apex,
                hr.property_name,
                hr.property_id,
                hr.property_version,
            ]
            for hr in host_records
        ],
    )

    write_csv(
        os.path.join(out_dir, "cps_certs.csv"),
        ["enrollment_id", "common_name", "sans", "status", "network"],
        cps_rows,
    )

    write_csv(
        os.path.join(out_dir, "appsec_summary.csv"),
        ["config_id", "config_name", "latest_version", "num_policies"],
        appsec_rows,
    )

    if args.include_products:
        for filename, rows in products_rows.items():
            headers = {
                "edgedns_zones.csv": ["zone", "type_or_contract", "status"],
                "gtm_domains.csv": ["gtm_domain"],
                "edgeworkers.csv": [
                    "edgeworker_id",
                    "name",
                    "group_id",
                    "last_modified",
                ],
                "cloudlets_policies.csv": [
                    "policy_id",
                    "name",
                    "cloudlet_type",
                    "status",
                ],
                "cloud_wrapper.csv": ["id", "name", "status"],
            }[filename]
            write_csv(os.path.join(out_dir, filename), headers, rows)

        # GTM deep export per domain
        for domain in gtm_domains:
            base_dir = os.path.join(out_dir, "gtm", domain)
            ensure_dir(base_dir)

            dcs = gtm_list_datacenters(api, domain)
            write_csv(
                os.path.join(base_dir, "datacenters.csv"),
                [
                    "datacenterId",
                    "nickname",
                    "city",
                    "stateOrProvince",
                    "country",
                    "continent",
                    "latitude",
                    "longitude",
                    "virtual",
                    "cloneOf",
                    "scorePenalty",
                    "weight",
                ],
                [
                    [
                        dc.get("datacenterId"),
                        dc.get("nickname"),
                        dc.get("city"),
                        dc.get("stateOrProvince"),
                        dc.get("country"),
                        dc.get("continent"),
                        dc.get("latitude"),
                        dc.get("longitude"),
                        dc.get("virtual"),
                        dc.get("cloneOf"),
                        dc.get("scorePenalty"),
                        dc.get("weight"),
                    ]
                    for dc in dcs
                ],
            )
            write_json(os.path.join(base_dir, "datacenters.json"), dcs)

            ltests = gtm_list_liveness_tests(api, domain)
            write_csv(
                os.path.join(base_dir, "liveness_tests.csv"),
                [
                    "name",
                    "testInterval",
                    "testObject",
                    "testObjectProtocol",
                    "testObjectPort",
                    "testTimeout",
                    "httpError3xx",
                    "httpError4xx",
                    "httpError5xx",
                    "requestString",
                    "responseString",
                    "peerCertificateVerification",
                ],
                [
                    [
                        lt.get("name"),
                        lt.get("testInterval"),
                        lt.get("testObject"),
                        lt.get("testObjectProtocol"),
                        lt.get("testObjectPort"),
                        lt.get("testTimeout"),
                        lt.get("httpError3xx"),
                        lt.get("httpError4xx"),
                        lt.get("httpError5xx"),
                        lt.get("requestString"),
                        lt.get("responseString"),
                        lt.get("peerCertificateVerification"),
                    ]
                    for lt in ltests
                ],
            )
            write_json(os.path.join(base_dir, "liveness_tests.json"), ltests)

            cidr_maps = gtm_list_cidr_maps(api, domain)
            as_maps = gtm_list_as_maps(api, domain)
            geo_maps = gtm_list_geo_maps(api, domain)
            write_csv(
                os.path.join(base_dir, "cidr_maps.csv"),
                ["name", "defaultDatacenter", "assignmentsCount"],
                [
                    [
                        m.get("name"),
                        (m.get("defaultDatacenter") or {}).get("datacenterId"),
                        len(m.get("assignments", []) or []),
                    ]
                    for m in cidr_maps
                ],
            )
            write_csv(
                os.path.join(base_dir, "as_maps.csv"),
                ["name", "defaultDatacenter", "assignmentsCount"],
                [
                    [
                        m.get("name"),
                        (m.get("defaultDatacenter") or {}).get("datacenterId"),
                        len(m.get("assignments", []) or []),
                    ]
                    for m in as_maps
                ],
            )
            write_csv(
                os.path.join(base_dir, "geo_maps.csv"),
                ["name", "defaultDatacenter", "assignmentsCount"],
                [
                    [
                        m.get("name"),
                        (m.get("defaultDatacenter") or {}).get("datacenterId"),
                        len(m.get("assignments", []) or []),
                    ]
                    for m in geo_maps
                ],
            )
            write_json(os.path.join(base_dir, "cidr_maps.json"), cidr_maps)
            write_json(os.path.join(base_dir, "as_maps.json"), as_maps)
            write_json(os.path.join(base_dir, "geo_maps.json"), geo_maps)

            props = gtm_list_properties(api, domain)
            props_rows: List[List[Any]] = []
            for p in props:
                pname = p.get("propertyName") or p.get("name")
                pfull = gtm_get_property(api, domain, pname) if pname else {}
                props_rows.append(
                    [
                        pname,
                        p.get("type"),
                        p.get("ipv6") or p.get("ipv6"),
                        p.get("handoutMode"),
                        p.get("failoverOrder"),
                        p.get("healthThreshold"),
                        (p.get("geoMap") or {}).get("name"),
                        (p.get("asMap") or {}).get("name"),
                        (p.get("cidrMap") or {}).get("name"),
                        p.get("ttl"),
                        len((pfull.get("trafficTargets") or [])),
                    ]
                )
                targets = pfull.get("trafficTargets") or []
                write_csv(
                    os.path.join(base_dir, f"property_{pname}_targets.csv"),
                    [
                        "datacenterId",
                        "enabled",
                        "weight",
                        "servers",
                        "handoutCName",
                        "name",
                    ],
                    [
                        [
                            t.get("datacenterId"),
                            t.get("enabled"),
                            t.get("weight"),
                            ";".join(t.get("servers", [])),
                            t.get("handoutCName"),
                            t.get("name"),
                        ]
                        for t in targets
                    ],
                )
                write_json(os.path.join(base_dir, f"property_{pname}.json"), pfull)

            write_csv(
                os.path.join(base_dir, "properties.csv"),
                [
                    "propertyName",
                    "type",
                    "ipv6",
                    "handoutMode",
                    "failoverOrder",
                    "healthThreshold",
                    "geoMap",
                    "asMap",
                    "cidrMap",
                    "ttl",
                    "trafficTargetsCount",
                ],
                props_rows,
            )

    # Markdown checklists per apex
    host_by_apex: Dict[str, List[HostnameRecord]] = defaultdict(list)
    for hr in host_records:
        host_by_apex[hr.apex].append(hr)
    checklists_dir = os.path.join(out_dir, "checklists")
    for apex, records in host_by_apex.items():
        content = generate_checklist(apex, records, parsed_by_property, cps_by_sni)
        write_text(os.path.join(checklists_dir, f"{apex}.md"), content)

    print(f"Wrote reports to {os.path.abspath(out_dir)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
