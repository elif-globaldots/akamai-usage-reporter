#!/usr/bin/env python3
"""
Find valid contract-group combinations for PAPI calls.
"""

import os
import sys
import requests
import json


def load_env_file():
    """Load environment variables from akamai.env file."""
    env_file = os.path.join(os.path.dirname(__file__), "akamai.env")
    if os.path.exists(env_file):
        print(f"Loading environment variables from {env_file}")
        with open(env_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key] = value
                    print(f"Loaded: {key}")
        return True
    else:
        print(f"Environment file not found: {env_file}")
        return False


def find_valid_combinations():
    """Find valid contract-group combinations."""

    if not load_env_file():
        return False

    host = os.environ.get("AKAMAI_HOST")
    client_token = os.environ.get("AKAMAI_CLIENT_TOKEN")
    client_secret = os.environ.get("AKAMAI_CLIENT_SECRET")
    access_token = os.environ.get("AKAMAI_ACCESS_TOKEN")

    if not all([host, client_token, client_secret, access_token]):
        print("❌ Missing credentials!")
        return False

    try:
        from akamai.edgegrid import EdgeGridAuth

        session = requests.Session()
        session.auth = EdgeGridAuth(
            client_token=client_token,
            client_secret=client_secret,
            access_token=access_token,
        )

        print("\n=== Finding Valid Contract-Group Combinations ===")

        # Get all contracts
        contracts_url = f"https://{host}/papi/v1/contracts"
        contracts_response = session.get(contracts_url, timeout=30)

        if contracts_response.status_code != 200:
            print(f"❌ Failed to get contracts: {contracts_response.status_code}")
            return False

        contracts_data = contracts_response.json()
        contracts = contracts_data.get("contracts", {}).get("items", [])
        print(f"Found {len(contracts)} contracts")

        # Get all groups
        groups_url = f"https://{host}/papi/v1/groups"
        groups_response = session.get(groups_url, timeout=30)

        if groups_response.status_code != 200:
            print(f"❌ Failed to get groups: {groups_response.status_code}")
            return False

        groups_data = groups_response.json()
        groups = groups_data.get("groups", {}).get("items", [])
        print(f"Found {len(groups)} groups")

        # Find valid combinations
        valid_combinations = []

        for contract in contracts:
            contract_id = contract.get("contractId")
            contract_type = contract.get("contractTypeName", "Unknown")

            print(f"\n--- Testing Contract: {contract_id} ({contract_type}) ---")

            for group in groups:
                group_id = group.get("groupId")
                group_name = group.get("groupName", "Unknown")
                group_contracts = group.get("contractIds", [])

                # Check if this group can be used with this contract
                if contract_id in group_contracts:
                    print(
                        f"  ✓ Group {group_id} ({group_name}) matches contract {contract_id}"
                    )

                    # Test if this combination works for properties
                    print(f"    Testing Properties API...")
                    properties_url = f"https://{host}/papi/v1/properties"
                    params = {"contractId": contract_id, "groupId": group_id}

                    try:
                        properties_response = session.get(
                            properties_url, params=params, timeout=30
                        )

                        if properties_response.status_code == 200:
                            properties_data = properties_response.json()
                            properties = properties_data.get("properties", {}).get(
                                "items", []
                            )
                            print(f"    ✅ SUCCESS! Found {len(properties)} properties")

                            valid_combinations.append(
                                {
                                    "contractId": contract_id,
                                    "contractType": contract_type,
                                    "groupId": group_id,
                                    "groupName": group_name,
                                    "propertiesCount": len(properties),
                                }
                            )
                        else:
                            print(f"    ❌ Failed: {properties_response.status_code}")

                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                else:
                    print(
                        f"  ✗ Group {group_id} ({group_name}) does NOT match contract {contract_id}"
                    )
                    print(f"    Group contracts: {group_contracts}")

        # Summary
        print("\n=== Valid Combinations Found ===")
        if valid_combinations:
            for combo in valid_combinations:
                print(f"✅ Contract: {combo['contractId']} ({combo['contractType']})")
                print(f"   Group: {combo['groupId']} ({combo['groupName']})")
                print(f"   Properties: {combo['propertiesCount']}")
                print()

            print(f"Total valid combinations: {len(valid_combinations)}")
            return valid_combinations
        else:
            print("❌ No valid contract-group combinations found!")
            print("This suggests a deeper permission or configuration issue.")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main function."""
    print("Valid Contract-Group Combinations Finder")
    print("=" * 45)

    combinations = find_valid_combinations()

    if combinations:
        print("\n🎉 Found working combinations!")
        print("Use one of these in your script.")
    else:
        print("\n💥 No working combinations found.")
        print("\nPossible issues:")
        print("1. API client scope restrictions")
        print("2. Account configuration issues")
        print("3. Network/firewall restrictions")
        print("4. Akamai support needed")


if __name__ == "__main__":
    main()
