# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
