# Ignition SCADA Tag Bulk Uploader — Implementation Plan

> **Status**: Phase 0 COMPLETE — Proceeding to Phase 1
> **Architecture Decision**: User-facing interface will be a **REST API** (Ktor). ✅ DECIDED
> **Integration Decision**: Gateway REST API — `POST /data/api/v1/tags/import` (Approach A). ✅ DECIDED
> **Critical Issue**: ~~How tags are created in Ignition is still unverified.~~ **RESOLVED** — Tag import endpoint confirmed via OpenAPI spec.
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

## Phase 1: Prototype the Confirmed Approach

**Goal**: Build a minimal working prototype that creates ONE tag programmatically AND accepts a file via REST API.

### 1.1 REST API Skeleton (all approaches)
1. Set up Kotlin/Gradle project with Ktor server
2. Implement `POST /api/upload` — accepts a hardcoded test file, returns JSON
3. Implement `GET /api/health` — returns service status
4. Verify the API starts and responds

### 1.2 Ignition Integration (depends on chosen approach)

#### Approach A (Ignition REST API — Tag Import Endpoint) ✅ SELECTED
1. Generate an API token via `POST /data/api/v1/api-token/generate`
2. Create the token resource in Ignition via `POST /data/api/v1/resources/ignition/api-token`
3. Determine the exact auth header format (test `Authorization: Bearer <key>` and `Authorization: api-key <key>`)
4. Export an existing tag via `GET /data/api/v1/tags/export?provider=default&type=json` to capture the **exact JSON format**
5. Construct a minimal tag JSON payload (one OPC tag) matching the export format
6. POST to `/data/api/v1/tags/import?provider=default&type=json&collisionPolicy=Overwrite`
7. Parse the QualityCode response — empty array = success
8. Verify the tag appears in Ignition Designer
9. **Bonus**: Test CSV import format — export JSON, manually create equivalent CSV, import via `type=csv`, compare results

#### ~~If Approach B (Module SDK)~~ — Not needed
#### ~~If Approach C (Scripting Bridge)~~ — Not needed

### Prototype Deliverables:
- [ ] Ktor REST API starts and accepts file upload at `POST /api/upload`
- [ ] One tag created successfully via chosen Ignition mechanism
- [ ] Authentication method confirmed and documented
- [ ] Request/response format documented
- [ ] Error handling for common failures documented
- [ ] Tag data types and path format confirmed

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

## Technology Stack

**Core (independent of Ignition approach)**:
- Language: Kotlin
- Build: Gradle (Kotlin DSL) with version catalog
- REST API: Ktor Server (Core + Netty + Content Negotiation + Jackson)
- Spreadsheet: Apache POI + OpenCSV
- JSON: Jackson + Kotlin module
- Logging: SLF4J + Logback
- Testing: JUnit 5 + MockK + Ktor Test Client
- JVM: Java 11+

**Ignition Integration**:
- HTTP Client: Ktor Client (CIO engine) for outbound calls to Ignition Gateway — avoids a separate OkHttp dependency since Ktor is already in use

**Note**: Use current dependency versions. Previous plan pinned 2023-era versions.

---

## Deployment

**Primary**: Containerized REST API service
- Dockerfile with JVM + fat JAR (Gradle Shadow plugin)
- `application.conf` (HOCON) for Ktor server configuration
- Environment variables for Ignition credentials
- Docker Compose for local development

**Configuration** (`application.conf`):
```hocon
ktor {
    deployment {
        port = 8080
    }
    application {
        modules = [ com.scada.taguploader.ApplicationKt.module ]
    }
}

ignition {
    gateway {
        url = ${?IGNITION_GATEWAY_URL}
        timeout = 30000
        retries = 3
    }
    auth {
        # The API key (not the hash) — this is the credential sent with each request.
        # Generated via POST /data/api/v1/api-token/generate (the "key" field).
        apiKey = ${?IGNITION_API_KEY}
    }
}

upload {
    maxFileSize = 10485760  # 10MB
    defaultEncoding = "UTF-8"
}
```

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
