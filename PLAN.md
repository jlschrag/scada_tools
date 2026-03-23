# Ignition SCADA Tag Bulk Uploader — Implementation Plan

> **Status**: Phase 1 COMPLETE — Phase 1 POC delivered successfully
> **Architecture Decision**: User-facing interface will be a **REST API** (FastAPI + Python). ✅ IMPLEMENTED
> **Integration Decision**: Gateway REST API — `POST /data/api/v1/tags/import` (Approach A). ✅ IMPLEMENTED
> **Critical Issue**: ~~How tags are created in Ignition is still unverified.~~ **RESOLVED** — Tag import endpoint confirmed and working
> **Technology Change**: Originally planned Kotlin/Ktor, implemented with Python/FastAPI for rapid prototyping and developer familiarity
> **Last Updated**: 2026-03-23

---

## Phase 0: Research & Verification (✅ COMPLETE)

**Goal**: Determine which tag-creation mechanism to use, with evidence.

Three approaches were evaluated:

| Approach | Mechanism | Result |
|----------|-----------|--------|
| **A. Gateway REST API** | HTTP POST to `POST /data/api/v1/tags/import` | ✅ **SELECTED** — confirmed via OpenAPI spec |
| **B. Module SDK** | Java/Kotlin code using `TagManager`/`TagProvider` | ❌ Not needed |
| **C. Scripting Bridge** | Call `system.tag.configure()` via WebDev module | ❌ Not needed |

### Decision Gate

| Question | Answer |
|----------|--------|
| Does the OpenAPI have a tag creation endpoint? | **YES** — `POST /data/api/v1/tags/import` |
| What is the endpoint path and method? | `POST /data/api/v1/tags/import?provider=<name>&type=json&collisionPolicy=<policy>&path=<optional>` |
| Does `system.tag.configure()` work for our use case? | Yes, but **not needed** — REST API is sufficient |
| Do we need a full Ignition Module? | **NO** |
| **Chosen approach**: | **A — Gateway REST API (Tag Import endpoint)** |

### Key Findings
- **Import endpoint**: Accepts `application/octet-stream` body (tag export file bytes) with query params for `provider`, `type` (json/xml/csv), `collisionPolicy`, and optional `path`
- **Export endpoint**: `GET /data/api/v1/tags/export` produces JSON or XML — use this to capture the exact tag format for constructing import payloads
- **Authentication**: API Token key/hash pair via `POST /data/api/v1/api-token/generate`
- **Response**: `List<QualityCode>` — empty array = success, non-empty = errors with `{ level, userCode, diagnosticMessage }`
- **Collision policies**: `Abort`, `Overwrite`, `Rename`, `Ignore`, `MergeOverwrite`

### Fallback Plan
If Phase 1 prototyping reveals the import endpoint can't handle the use case (e.g., the JSON structure is impractical to generate, or auth doesn't work as expected), fall back to **Approach C** (WebDev module + `system.tag.configure()`). This is well-documented and provides individual tag creation with explicit error handling per tag. Approach B (Module SDK) is a last resort due to packaging/signing complexity.

See `CONTEXT.md` for full research details.

---

## Phase 1: Prototype the Confirmed Approach (✅ COMPLETE)

**Goal**: Build a minimal working prototype that creates ONE tag programmatically AND accepts a file via REST API.

**Technology Decision**: Implemented with **Python + FastAPI** instead of Kotlin/Ktor for rapid prototyping, developer familiarity, and ease of deployment. Python's ecosystem (httpx, pydantic, uvicorn) provides excellent async HTTP support and data validation.

### 1.1 REST API Skeleton ✅ DELIVERED
1. ✅ Set up Python project with FastAPI server
2. ✅ Implement `POST /api/upload` — accepts file upload, creates test tag
3. ✅ Implement `GET /api/health` — returns service status and Ignition connectivity
4. ✅ Implement `GET /` — API information endpoint
5. ✅ Interactive API docs at `/docs` (automatic via FastAPI/OpenAPI)

### 1.2 Ignition Integration ✅ DELIVERED

#### Approach A (Ignition REST API — Tag Import Endpoint) ✅ IMPLEMENTED
1. ✅ Generate an API token via `POST /data/api/v1/api-token/generate`
2. ✅ Confirmed auth header format: `Authorization: Bearer <key>`
3. ✅ Implemented tag export support via `GET /data/api/v1/tags/export` (utility method)
4. ✅ Construct minimal tag JSON payload (OPC tag) matching Ignition export format
5. ✅ POST to `/data/api/v1/tags/import` with proper headers and collision policy
6. ✅ Parse QualityCode response — empty array = success
7. ✅ Connection pooling with shared httpx.AsyncClient
8. ✅ Token refresh on 401 (automatic retry with new token)

### Prototype Deliverables:
- ✅ FastAPI REST API starts and accepts file upload at `POST /api/upload`
- ✅ One tag created successfully via Ignition REST API
- ✅ Authentication method confirmed: Bearer token with auto-refresh
- ✅ Request/response format documented in Pydantic models
- ✅ Error handling for common failures (file size, connectivity, auth)
- ✅ Tag data types and path format confirmed (AtomicTag, Int4, OPC)
- ✅ Logging with Python logging module (replaced print statements)
- ✅ Security hardening (no credential leaks, generic error messages)
- ✅ CORS support for browser clients
- ✅ File type validation (.csv, .xlsx, .xls)
- ✅ Configurable settings via environment variables

---

## Phase 2: Full Implementation

**Only proceed after Phase 1 prototype is working.**

### 2.1 Core Infrastructure (1–2 days)
1. Gradle project with all dependencies
2. Data models: `TagDefinition`, `UploadRequest`, `UploadResponse`, `ValidationResult`
3. Exception hierarchy
4. Logging (SLF4J + Logback)

### 2.2 Spreadsheet Parsing (2 days)
1. `SpreadsheetParser` interface
2. CSV parser (OpenCSV)
3. XLSX parser (Apache POI)
4. XLS parser (Apache POI)
5. Factory pattern for format detection
6. Header validation
7. Unit tests with sample files

### 2.3 Validation & Type Mapping (1–2 days)
1. `TagValidator` — name rules, required fields, duplicates
2. `DataTypeMapper` — user-friendly names → Ignition type IDs
3. Address format validation (based on Phase 0 research)
4. Detailed error reporting with row/column info

### 2.4 Tag Creation Client (2 days)
1. `IgnitionImportClient` — uses `POST /data/api/v1/tags/import` endpoint
   - Takes a list of `TagDefinition`, serializes to Ignition JSON export format
   - POSTs as `application/octet-stream` with `type=json`
2. Authentication handling — API Token key (generated via `/data/api/v1/api-token/generate`)
3. Collision policy mapping (⚠️ **verify in Phase 1** — `Overwrite` vs `MergeOverwrite` semantics need testing):
   - `DuplicateStrategy.SKIP` → `Ignore`
   - `DuplicateStrategy.UPDATE` → `Overwrite` (replaces tag entirely) or `MergeOverwrite` (merges folder structure, overwrites conflicting tags) — **Phase 1 must test both to determine correct mapping**
   - `DuplicateStrategy.FAIL` → `Abort`
4. Response parsing — `List<QualityCode>` with `{ level, userCode, diagnosticMessage }`
   - Empty array = all tags imported successfully
   - Non-empty = report errors. **Note**: It is unknown whether QualityCodes map 1:1 to individual tags or are aggregated. Phase 1 must test with intentional failures to determine granularity.
   - **Fallback if no per-tag mapping**: Report all QualityCodes as batch-level errors, mark all tags as "status unknown," and include the raw diagnosticMessages in the response. Users would need to verify in Ignition Designer.
5. Retry logic with exponential backoff
6. Batching strategy — one POST with all tags; for very large imports (10k+), chunk into multiple POSTs
7. Integration tests against mock or real Gateway

### 2.5 Orchestrator (1 day)
1. `TagUploader` — coordinates parse → validate → create
2. Invoked by the REST API endpoint handler (not a main function)
3. Result aggregation (success/failure counts)
4. Error strategy: The import endpoint is atomic (single POST), so fail-fast vs continue only applies to **validation** (stop on first validation error vs collect all). The `onError` config controls validation behavior, not import behavior. If validation passes, the import is all-or-nothing per batch.
5. Idempotency handling via collision policy (skip existing, update, or fail on duplicates — configurable)
6. For very large imports (10k+), the orchestrator chunks into multiple POSTs. `onError` then also controls whether to abort remaining chunks after a failed batch.

### 2.6 REST API Layer (1–2 days)
1. Ktor server with Netty engine
2. Endpoints:
   - `POST /api/upload` — multipart file upload (accepts CSV, XLS, XLSX)
     - Request: multipart form data with `file` part + optional JSON config
     - Config fields: `gatewayUrl`, `tagProvider`, `basePath`, `dryRun`, `onError` (continue|stop — controls validation and multi-batch behavior), `onDuplicate` (skip|update|fail), `encoding`
     - Response: JSON with validation results, per-tag success/failure, summary counts
   - `GET /api/health` — health check (returns service status + Ignition connectivity)
   - `GET /api/types` — list supported Ignition data types
3. Content negotiation (Jackson JSON)
4. File size limits (configurable, default 10MB)
5. Input validation and error responses (proper HTTP status codes)
6. CORS configuration (for browser-based clients)
7. Request logging

### 2.7 Testing & Documentation (2 days)
1. Unit tests (>80% coverage)
2. API integration tests using Ktor test client
3. Integration tests with mock Ignition Gateway
4. Sample spreadsheets (CSV, XLSX, XLS)
5. OpenAPI/Swagger spec for our REST API
6. README with usage examples (curl, Postman)
7. Troubleshooting guide

**Estimated total for Phase 2: ~11 days**

---

## REST API Contract

### `POST /api/upload`

**Request** (multipart/form-data):
```
file: <spreadsheet file> (required, max 10MB)
config: <JSON string> (optional)
```

Config JSON:
```json
{
  "gatewayUrl": "https://ignition.example.com:8043",
  "tagProvider": "default",
  "basePath": "Facility/Zone1",
  "dryRun": false,
  "onError": "continue",
  "onDuplicate": "skip",
  "opcServer": "Ignition OPC UA Server",
  "encoding": "UTF-8"
}
```

**Response** (application/json):
```json
{
  "status": "completed",
  "summary": {
    "totalRows": 150,
    "successful": 148,
    "failed": 2,
    "skipped": 0
  },
  "results": [
    { "row": 1, "name": "Temperature_Zone1", "status": "created" },
    { "row": 2, "name": "Pressure_Zone1", "status": "created" },
    { "row": 3, "name": "BadTag!", "status": "failed", "error": "Invalid tag name: contains '!'" }
  ],
  "validationErrors": [
    { "row": 3, "field": "name", "value": "BadTag!", "message": "Invalid tag name: contains '!'" }
  ]
}
```

### `POST /api/upload` (dry run)

Same request with `"dryRun": true` in config. Response has `"status": "validated"` and no tags are created. Only validation results are returned.

### `GET /api/health`

**Response**:
```json
{
  "status": "healthy",
  "ignitionConnected": true,
  "ignitionGateway": "https://ignition.example.com:8043",
  "version": "1.0.0"
}
```

### `GET /api/types`

**Response**:
```json
{
  "dataTypes": [
    { "id": "Boolean", "aliases": ["bool", "boolean"] },
    { "id": "Integer", "aliases": ["int", "integer", "int4"] },
    { "id": "Float", "aliases": ["float", "real", "float4"] },
    { "id": "Double", "aliases": ["double", "float8"] },
    { "id": "String", "aliases": ["string", "text", "varchar"] },
    { "id": "DateTime", "aliases": ["datetime", "timestamp", "date"] },
    { "id": "Long", "aliases": ["long", "int8", "bigint"] }
  ]
}
```

---

## Data Models

```kotlin
// === Domain Models ===

data class TagDefinition(
    val name: String,                           // Required: tag name
    val path: String = "",                      // Tag folder path (e.g., "Facility/Zone1")
    val opcItemPath: String,                    // Required: device-relative OPC item path (e.g., "[PLC1]Zone1/Temp")
    val opcServer: String = "",                 // OPC server name (if not embedded in item path)
    val dataType: String,                       // Required: int, float, string, bool, etc.
    val description: String? = null,            // Optional: tag description
    val enabled: Boolean = true,                // Optional: tag enabled state
    val sourceIndex: Int = 0,                   // Track original row for error reporting
    val additionalProperties: Map<String, Any?> = emptyMap()
)

// === API Request/Response Models ===

data class UploadConfig(
    val gatewayUrl: String? = null,             // Override default gateway URL
    val tagProvider: String = "default",        // Ignition tag provider
    val basePath: String = "",                  // Tag folder prefix
    val dryRun: Boolean = false,                // Validate only, don't create
    val onError: ErrorStrategy = ErrorStrategy.CONTINUE,
    val onDuplicate: DuplicateStrategy = DuplicateStrategy.SKIP,
    val encoding: String = "UTF-8"
)

enum class ErrorStrategy { CONTINUE, STOP }  // Controls validation and multi-batch behavior (not single import — that's atomic)
enum class DuplicateStrategy { SKIP, UPDATE, FAIL }

data class UploadResponse(
    val status: String,                         // "completed", "validated", "failed"
    val summary: UploadSummary,
    val results: List<TagResult>,
    val validationErrors: List<ValidationError>
)

data class UploadSummary(
    val totalRows: Int,
    val successful: Int,
    val failed: Int,
    val skipped: Int
)

data class TagResult(
    val row: Int,
    val name: String,
    val status: String,                         // "created", "updated", "skipped", "failed", "unknown"
    val error: String? = null
)
// Note: If the import endpoint doesn't provide per-tag granularity in its QualityCode
// response, individual tag statuses may be "unknown" with batch-level errors reported
// in a separate `batchErrors` field on UploadResponse.

// === Validation Models ===

data class ValidationResult(
    val isValid: Boolean,
    val errors: List<ValidationError> = emptyList()
)

data class ValidationError(
    val rowIndex: Int,
    val field: String,
    val value: String,
    val message: String
)
```

---

## Technology Stack (As Implemented in Phase 1)

**Core**:
- Language: **Python 3.11+**
- REST API: **FastAPI** (async web framework)
- Server: **Uvicorn** (ASGI server with standard extras)
- HTTP Client: **httpx** (async HTTP client for Ignition API calls)
- Data Validation: **Pydantic** (models, settings, validation)
- JSON: Native Python + Pydantic serialization
- Logging: Python **logging** module (structured logging)
- Testing: **pytest** + **pytest-asyncio**
- File Parsing (Phase 2): Will use **pandas** (CSV/Excel) or **openpyxl** (XLSX)

**Configuration**:
- **pydantic-settings** for environment-based configuration
- **python-dotenv** for .env file support

**Deployment**:
- Docker container with Python runtime
- docker-compose for local development with Ignition Gateway

**Note**: Phase 1 uses compatible version ranges (e.g., `fastapi>=0.109.0,<1.0`) to allow patch updates while maintaining compatibility.

---

## Deployment (Phase 1 Implementation)

**Primary**: Python application with virtual environment or Docker container

**Local Development**:
1. Clone repository
2. Run `./run.sh` which:
   - Creates virtual environment
   - Installs dependencies from `requirements.txt`
   - Creates `.env` from `.env.example` (with warnings)
   - Starts uvicorn server with auto-reload

**Docker Deployment** (Phase 2):
- Dockerfile with Python runtime + dependencies
- Multi-stage build for smaller images
- docker-compose.yml for local dev with Ignition Gateway

**Configuration** (`.env` file):
```bash
# API Server
API_HOST=0.0.0.0
API_PORT=8080
API_RELOAD=False
LOG_LEVEL=INFO

# Ignition Gateway (REQUIRED)
IGNITION_GATEWAY_URL=http://localhost:8088
IGNITION_USERNAME=admin  # CHANGE THIS
IGNITION_PASSWORD=password  # CHANGE THIS
IGNITION_VERIFY_SSL=False

# Tag Provider
TAG_PROVIDER=default
OPC_SERVER_NAME=Ignition OPC UA Server

# Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_EXTENSIONS=[".csv",".xlsx",".xls"]
```

**Security Notes**:
- Credentials are **required** (no defaults in code)
- Application fails fast if credentials not provided
- Credentials never logged (even in debug mode)
- Generic error messages to API clients (details logged server-side)

---

## Success Criteria

- [ ] **Phase 0**: Tag creation mechanism confirmed with evidence
- [ ] **Phase 1**: REST API accepts file upload and creates one tag end-to-end
- [ ] **Phase 2**: Bulk creation from spreadsheet (1000+ tags) via API
- [ ] `POST /api/upload` accepts CSV, XLS, XLSX and returns structured JSON
- [ ] `GET /api/health` reports service and Ignition connectivity status
- [ ] Dry-run mode validates without creating tags
- [ ] Detailed error reporting with row numbers in response
- [ ] Idempotency strategy implemented (skip/update/fail on duplicates)
- [ ] Comprehensive test coverage (>80%)
- [ ] OpenAPI/Swagger spec for our REST API
- [ ] Docker deployment working
- [ ] Secure credential handling (HTTPS enforced by default for Ignition calls)

## Timeline Estimate
- Phase 0: 1–3 days (research — may require live Ignition instance)
- Phase 1: 2–3 days (REST API skeleton + Ignition prototype)
- Phase 2: ~11 days (full implementation)
- **Total**: ~16–17 days of development time
