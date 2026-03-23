# Changelog

All notable changes to the Ignition SCADA Tag Bulk Uploader project.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.0] - 2026-03-23 - Phase 1 POC Complete

### Added

#### Core Infrastructure
- FastAPI application with Python 3.11+ support
- Configuration management via pydantic-settings and environment variables
- Pydantic models for request/response validation
- httpx async HTTP client for Ignition Gateway integration

#### API Endpoints
- `GET /api/health` - Health check endpoint
  - Returns service status
  - Checks Ignition Gateway connectivity
  - Reports Gateway URL and connection status
- `POST /api/upload` - File upload endpoint (POC implementation)
  - Accepts file upload via multipart/form-data
  - File size validation (10MB limit)
  - Creates hardcoded test tag for POC demonstration

#### Ignition Gateway Integration
- API token generation (`POST /data/api/v1/api-token/generate`)
  - Username/password authentication
  - Returns key and hash
  - Bearer token auth for subsequent requests
- Tag import functionality (`POST /data/api/v1/tags/import`)
  - JSON tag format support
  - Collision policy support (Overwrite, Ignore, etc.)
  - QualityCode response parsing
  - Empty array = success detection
- Tag export capability (`GET /data/api/v1/tags/export`)
  - For discovering tag JSON format
  - JSON export type support
- Test tag creation with minimal required fields
  - OPC UA tag type
  - Int4 data type
  - Configurable tag name and path

#### Configuration
- Environment-based configuration (.env support)
- Configurable Ignition Gateway URL
- SSL verification toggle (for self-signed certificates)
- Configurable tag provider name
- File upload size limits

#### Documentation
- Comprehensive Phase 1 README (PHASE1_README.md)
  - Complete API documentation
  - Ignition integration findings
  - Testing workflow
  - Troubleshooting guide
- Updated main README with Quick Start guide
- PLAN.md with full roadmap
- Example CSV file (sample_tags.csv)
- Examples directory with README

#### Development Tools
- requirements.txt with pinned dependencies
- pyproject.toml for modern Python tooling
- .env.example template
- .gitignore for Python projects
- docker-compose.yml for Ignition test environment
- run.sh quick start script
- test_phase1.py manual test suite

#### Testing
- Manual test script (test_phase1.py)
  - Connectivity test
  - API token generation test
  - Tag creation test
  - Summary reporting

### Documented

#### Phase 1 Findings
- ✅ API token generation mechanism confirmed
- ✅ Bearer token authentication working
- ✅ Tag import endpoint JSON format documented
- ✅ QualityCode response format captured
- ✅ Collision policies identified
- ✅ Minimum tag fields determined
- ✅ SSL verification handling for self-signed certs

#### Known Limitations
- File upload does not parse spreadsheet content (Phase 2)
- Creates only one hardcoded test tag per upload
- No validation of tag definitions
- No bulk import capability
- No per-tag error reporting granularity

### Changed
- Switched from Kotlin/Ktor to Python/FastAPI (per user request)
- Using httpx instead of Ktor Client for HTTP requests
- Using Pydantic instead of kotlinx.serialization for data models

## [Unreleased] - Phase 2

### Planned Features

#### Spreadsheet Parsing
- CSV parser (Python csv module)
- Excel parser (openpyxl for XLSX, xlrd for XLS)
- Auto-detect file format
- Header row validation
- Column mapping

#### Validation
- Tag name validation (character rules, length limits)
- Required fields verification
- Data type validation and mapping
- OPC item path format validation
- Duplicate tag detection

#### Bulk Import
- Process multiple tags from spreadsheet rows
- Batch import with progress tracking
- Per-tag success/failure reporting
- Error aggregation and reporting
- Dry-run mode (validation only, no import)

#### Configuration
- Upload configuration options (JSON payload)
  - `basePath` - Prefix for all tag paths
  - `dryRun` - Validate without creating
  - `onError` - Continue or stop on error
  - `onDuplicate` - Skip, update, or fail
  - `opcServer` - Default OPC server name
- Tag defaults from config

#### Enhanced Error Handling
- Row-level error reporting
- Field-level validation messages
- Ignition QualityCode mapping
- Detailed error summaries

#### Testing
- Unit tests with pytest
- Integration tests with mock Ignition
- Sample spreadsheet files
- End-to-end API tests
- Test coverage reporting

#### Production Readiness
- Logging configuration (structlog or loguru)
- Health check enhancements
- Rate limiting
- Request timeout handling
- Retry logic with exponential backoff
- Batch chunking for large imports (10k+ tags)

---

## Version History

- **v0.1.0** (2026-03-23) - Phase 1 POC Complete
- **v0.0.0** (2026-03-23) - Initial research (Phase 0)
