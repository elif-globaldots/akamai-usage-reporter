# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-01-XX

### Added
- **Rate Limiting Support**: Comprehensive analysis of Akamai rate limiting policies
- **Network Lists Analysis**: IP reputation lists, geographic restrictions, and custom network lists
- **Advanced Security Features**: Kona Site Defender, Prolexic DDoS, Client Reputation, Adaptive Security Engine
- **API Acceleration**: API Gateway, API Security, and API Rate Limiting support
- **Enhanced Migration Checklists**: Detailed guidance for migrating advanced Akamai features to Cloudflare

### Improved
- **Migration Planning**: More comprehensive coverage of Akamai features for Cloudflare migration
- **Security Analysis**: Better visibility into advanced security configurations
- **API Management**: Complete API-related feature discovery and documentation

### Technical
- New API endpoints for rate limiting, network lists, and advanced security
- Enhanced CSV output with additional product data
- Improved checklist generation with feature-specific migration guidance

## [1.1.0] - 2025-08-19

### Added
- **Auto-loading Environment**: Automatic loading of virtual environment and akamai.env file
- **Smart Contract-Group Detection**: Automatic detection of valid contract-group combinations
- **Comprehensive Debugging Tools**: Multiple diagnostic scripts for troubleshooting
- **Enhanced Error Handling**: Better error messages and debugging output
- **Environment File Template**: akamai.env.example for easy credential setup

### Fixed
- **PAPI Access Issues**: Resolved 403 Forbidden errors caused by contract-group mismatches
- **Environment Setup**: Eliminated need for manual virtual environment activation
- **Credential Management**: Streamlined setup process with automatic environment loading
- **API Compatibility**: Better handling of Akamai's contract-group requirements

### Improved
- **User Experience**: No more manual credential export or virtual environment activation
- **Debugging**: Added debug_papi.py, find_valid_combinations.py, and test_api_permissions.py
- **Documentation**: Updated SETUP.md with new auto-loading features
- **Error Messages**: More informative error output and troubleshooting guidance

### Technical
- Enhanced contract-group validation logic
- Improved API error handling and debugging
- Better environment variable management
- Streamlined authentication flow

## [1.0.0] - 2025-01-XX

### Added
- Initial release of Akamai Usage Reporter
- CLI tool for analyzing Akamai account usage
- Support for PAPI properties, hostnames, and rules parsing
- CPS certificate enrollment discovery
- AppSec configuration enumeration
- Edge DNS zone listing
- GTM domain discovery and deep export
- EdgeWorkers enumeration
- Cloudlets policies listing
- Cloud Wrapper container discovery
- Comprehensive CSV and JSON exports
- Markdown migration checklists per domain apex
- EdgeGrid authentication via environment variables
- Support for account switching

### Features
- **PAPI Analysis**: Properties, versions, hostnames, caching rules, redirects, headers, HSTS
- **SSL/CPS**: Certificate enrollments, CN/SANs, status, network deployment
- **GTM Deep Export**: Datacenters, properties, traffic targets, liveness tests, CIDR/Geo/AS maps
- **Additional Products**: Edge DNS, EdgeWorkers, Cloudlets, Cloud Wrapper
- **Migration Planning**: Structured checklists for Cloudflare migration
- **Flexible Output**: CSV summaries, JSON details, Markdown action items

### Technical
- Python 3.8+ compatibility
- EdgeGrid authentication
- Graceful API error handling
- Modular architecture for easy extension

