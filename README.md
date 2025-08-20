# Akamai Usage Reporter → Cloudflare Migration Checklist

[![CI](https://github.com/elif-globaldots/akamai-usage-reporter/workflows/CI/badge.svg)](https://github.com/elif-globaldots/akamai-usage-reporter/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://badge.fury.io/py/akamai-usage-reporter.svg)](https://badge.fury.io/py/akamai-usage-reporter)

A comprehensive CLI tool that analyzes your Akamai account (PAPI, AppSec, CPS, GTM, Edge DNS, EdgeWorkers, Cloudlets, Cloud Wrapper) and produces detailed migration checklists for Cloudflare.

## ✨ Features

- **🔍 Comprehensive Analysis**: Inventory PAPI properties, hostnames, SSL certificates, WAF rules, caching rules, and more
- **🌐 GTM Deep Export**: Detailed GTM domains, datacenters, properties, traffic targets, liveness tests, and maps
- **📊 Multiple Output Formats**: CSV summaries, JSON details, and Markdown migration checklists
- **🚀 Migration Planning**: Structured checklists per domain apex for Cloudflare migration
- **🔐 Secure Authentication**: EdgeGrid authentication via environment variables
- **📈 Extensible Architecture**: Easy to add support for additional Akamai products

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/elif-globaldots/akamai-usage-reporter.git
cd akamai-usage-reporter

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Set your Akamai EdgeGrid credentials as environment variables:

```bash
export AKAMAI_HOST="your-host.akamaiapis.net"
export AKAMAI_CLIENT_TOKEN="your-client-token"
export AKAMAI_CLIENT_SECRET="your-client-secret"
export AKAMAI_ACCESS_TOKEN="your-access-token"
export AKAMAI_ACCOUNT_SWITCH_KEY="your-account-switch-key"  # Optional
```

### Usage

```bash
# Basic usage
python -m akamai_usage_reporter --out-dir ./out

# Include rule parsing for caching/redirects/headers/HSTS
python -m akamai_usage_reporter --out-dir ./out --include-rules

# Full product inventory including GTM, Edge DNS, EdgeWorkers, etc.
python -m akamai_usage_reporter --out-dir ./out --include-rules --include-products
```

## 📁 Output Structure

```
out/
├── usage_summary.csv          # Properties and hostnames summary
├── hostnames.csv             # Detailed hostname mapping
├── cps_certs.csv            # SSL certificate enrollments
├── appsec_summary.csv       # WAF configurations
├── checklists/              # Migration checklists per domain
│   ├── example.com.md
│   └── another-domain.md
├── gtm_domains.csv          # GTM domains list
├── gtm/                     # Detailed GTM export per domain
│   └── example.com/
│       ├── datacenters.csv|json
│       ├── properties.csv
│       ├── liveness_tests.csv|json
│       ├── cidr_maps.csv|json
│       ├── geo_maps.csv|json
│       ├── as_maps.csv|json
│       └── property_<name>.json|_targets.csv
├── edgedns_zones.csv        # Edge DNS zones
├── edgeworkers.csv          # EdgeWorkers
├── cloudlets_policies.csv   # Cloudlets policies
├── cloud_wrapper.csv        # Cloud Wrapper containers
├── rate_limiting_policies.csv  # Rate limiting policies
├── network_lists.csv        # Network lists (IP reputation, geo restrictions)
├── kona_site_defender.csv   # Kona Site Defender configurations
├── prolexic_ddos.csv        # Prolexic DDoS protection settings
├── client_reputation.csv    # Client reputation policies
├── adaptive_security.csv    # Adaptive Security Engine rules
├── api_gateway.csv          # API Gateway configurations
├── api_security.csv         # API Security policies
└── api_rate_limiting.csv    # API Rate Limiting policies
```

## 🔧 Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--out-dir` | Output directory for reports | `./out` |
| `--include-rules` | Parse PAPI rules for behaviors | `False` |
| `--include-products` | Enumerate additional Akamai products | `False` |
| `--account-switch-key` | Akamai account switch key | From env var |
| `--edgerc-section` | Section in ~/.edgerc (placeholder) | `None` |

## 🌟 What Gets Analyzed

### Core PAPI Features
- **Properties**: All properties with versions and metadata
- **Hostnames**: CNAME mappings and SSL certificate status
- **Rules**: Caching behaviors, redirects, headers, HSTS settings
- **Behaviors**: Detailed parsing of property manager rules

### SSL & Security
- **CPS**: Certificate enrollment details, CN/SANs, status
- **AppSec**: WAF configurations and security policies
- **Edge DNS**: Zone configurations and settings

### Global Traffic Management (GTM)
- **Domains**: All GTM domains
- **Datacenters**: Physical and virtual datacenter locations
- **Properties**: GTM properties with traffic distribution
- **Traffic Targets**: Server assignments and weights
- **Liveness Tests**: Health check configurations
- **Maps**: CIDR, Geographic, and AS number mappings

### Additional Products
- **EdgeWorkers**: Edge computing functions and configurations
- **Cloudlets**: Policy-based traffic management
- **Cloud Wrapper**: Container configurations
- **Rate Limiting**: Traffic control policies and rules
- **Network Lists**: IP reputation lists, geographic restrictions, custom lists
- **Advanced Security**: Kona Site Defender, Prolexic DDoS, Client Reputation, Adaptive Security Engine
- **API Acceleration**: API Gateway, API Security, API Rate Limiting
- **Cloud Wrapper**: Container configurations

## 🎯 Cloudflare Migration Mapping

The generated checklists provide actionable steps for each domain:

1. **Zone Creation**: Create Cloudflare zone for each apex domain
2. **DNS Setup**: Configure nameservers or partial CNAME setup
3. **SSL Configuration**: Enable Universal SSL or upload custom certificates
4. **WAF Rules**: Recreate custom WAF rules and enable managed rules
5. **Cache Rules**: Convert Akamai caching behaviors to Cloudflare equivalents
6. **Redirects**: Use Transform Rules or Rulesets for redirects
7. **Headers**: Recreate header modifications
8. **HSTS**: Enable HTTP Strict Transport Security with matching settings

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Important Notes

- **API Access**: The tool's capabilities depend on your Akamai API client permissions
- **Graceful Degradation**: Missing data is handled gracefully with clear annotations
- **Security**: Never commit EdgeGrid credentials to version control
- **Testing**: Test in non-production environments first

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/elif-globaldots/akamai-usage-reporter/issues)
- **Discussions**: [GitHub Discussions](https://github.com/elif-globaldots/akamai-usage-reporter/discussions)
- **Documentation**: [Wiki](https://github.com/elif-globaldots/akamai-usage-reporter/wiki)

## 🙏 Acknowledgments

- Built with [Akamai EdgeGrid](https://developer.akamai.com/legacy/introduction/Client_Auth.html)
- Inspired by the need for comprehensive CDN migration tooling
- Community contributions and feedback

