# Ignition SCADA Tag Bulk Uploader — Implementation Plan

> **Status**: Phase 0 COMPLETE — Proceeding to Phase 1
> **Architecture Decision**: User-facing interface will be a **REST API** (Ktor). ✅ DECIDED
> **Integration Decision**: Gateway REST API — `POST /data/api/v1/tags/import` (Approach A). ✅ DECIDED
> **Critical Issue**: ~~How tags are created in Ignition is still unverified.~~ **RESOLVED** — Tag import endpoint confirmed via OpenAPI spec.
> **Last Updated**: 2026-03-23

---

## The Core Question

**How do you programmatically create tags in Ignition SCADA?**

There are three possible mechanisms. We must determine which one(s) work before writing any integration code.

| Approach | Mechanism | Deployment Model | Complexity |
|----------|-----------|-------------------|------------|
| **A. Gateway REST API** | HTTP POST to Ignition OpenAPI endpoint | REST API service (Ktor) + OkHttp outbound | Low |
| **B. Module SDK** | Java/Kotlin code using `TagManager`/`TagProvider` | Ignition Module with embedded REST API, or separate REST API service calling into module | High |
| **C. Scripting Bridge** | Call `system.tag.configure()` via WebDev module endpoint | REST API service (Ktor) + OkHttp to WebDev | Medium |

> **Note on Approach B**: If Phase 0 selects the Module SDK, the REST API may need to live *inside* the Ignition module (using Ignition's servlet context) or be a separate service that communicates with the module. This interaction will be designed during Phase 1 prototyping.

---

## Phase 0: Research & Verification (✅ COMPLETE)

**Goal**: Determine which tag-creation mechanism to use, with evidence.

### 0.1 Investigate the Ignition OpenAPI Specification

**What to check**:
1. Open a running Ignition 8.3 Gateway and navigate to the OpenAPI docs:
   - `https://<gateway>:8043/system/openapi.json` (or `/system/openapi.yaml`)
   - Gateway web UI → Status → OpenAPI section
   - Docs: https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi
2. Search the spec for any tag-related endpoints:
   - `tags`, `tag-config`, `tag-provider`, `tag-management`
   - Look for POST/PUT methods (not just GET)
3. Check if tag creation is listed or if the API is read-only for tags

**Expected finding**: Ignition's Gateway OpenAPI likely covers system status, licensing, alarming, auditing, and project resources — but **may NOT include tag creation**. The OpenAPI in Ignition 8.x has historically been limited in scope.

**Deliverable**: Document the exact endpoints available. If tag creation exists, record the path, method, request schema, and auth mechanism. If it doesn't exist, document that definitively.

### 0.2 Investigate `system.tag.configure()`

**What to check**:
1. Ignition scripting docs for `system.tag.configure()`:
   - https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-tag/system-tag-configure
2. This function is the **known, documented way** to create tags programmatically in Ignition
3. Determine:
   - Full function signature and parameters
   - JSON/dict structure for tag configuration
   - Whether it supports batch creation
   - What tag properties are required vs optional
   - How tag paths/folders work
   - Supported data types (the `dataType` enum values)
   - How OPC addresses are specified (`opcItemPath` property)
   - Error handling / return values

**Key detail**: `system.tag.configure()` runs inside Ignition's scripting environment (Jython). To call it from an external tool, we need a bridge — either:
- The **WebDev module** (exposes custom HTTP endpoints that can run scripts)
- A **custom Gateway module** (runs Java/Kotlin code with access to `GatewayContext`)
- The **Gateway Script Console** (manual, not automatable)

**Deliverable**: Document the exact function signature, tag configuration schema, and supported data types.

### 0.3 Investigate the Ignition Module SDK (if needed)

**What to check** (only if Approaches A and C are insufficient):
1. Ignition Module SDK docs:
   - https://www.docs.inductiveautomation.com/docs/8.3/developers/module-development
   - SDK GitHub: https://github.com/inductiveautomation/ignition-module-examples
2. Key interfaces:
   - `com.inductiveautomation.ignition.gateway.model.GatewayContext`
   - `com.inductiveautomation.ignition.common.tags.model.TagManager`
   - `com.inductiveautomation.ignition.common.tags.model.TagProvider`
   - `com.inductiveautomation.ignition.common.tags.config.TagConfiguration`
3. Module packaging: `.modl` file format, `module.xml` descriptor
4. Signing requirements (Ignition modules must be signed for production)

**Deliverable**: Document whether the Module SDK provides tag creation APIs and what the module packaging/deployment requirements are.

### 0.4 Decision Gate ✅ COMPLETE

| Question | Answer |
|----------|--------|
| Does the OpenAPI have a tag creation endpoint? | **YES** — `POST /data/api/v1/tags/import` |
| What is the endpoint path and method? | `POST /data/api/v1/tags/import?provider=<name>&type=json&collisionPolicy=<policy>&path=<optional>` |
| Does `system.tag.configure()` work for our use case? | Yes, but **not needed** — REST API is sufficient |
| Is the WebDev module available in the target environment? | **Not needed** — REST API is sufficient |
| Do we need a full Ignition Module? | **NO** |
| **Chosen approach**: | **A — Gateway REST API (Tag Import endpoint)** |

**Phase 0 complete. Proceeding to Phase 1.**

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
3. Collision policy mapping:
   - `DuplicateStrategy.SKIP` → `Ignore`
   - `DuplicateStrategy.UPDATE` → `MergeOverwrite`
   - `DuplicateStrategy.FAIL` → `Abort`
4. Response parsing — `List<QualityCode>` with `{ level, userCode, diagnosticMessage }`
   - Empty array = all tags imported successfully
   - Non-empty = report per-tag errors
5. Retry logic with exponential backoff
6. Batching strategy — one POST with all tags; for very large imports (10k+), chunk into multiple POSTs
7. Integration tests against mock or real Gateway

### 2.5 Orchestrator (1 day)
1. `TagUploader` — coordinates parse → validate → create
2. Invoked by the REST API endpoint handler (not a main function)
3. Result aggregation (success/failure counts per row)
4. Configurable error strategy (fail-fast vs continue-on-error)
5. Idempotency handling (skip existing, update, or fail on duplicates — configurable)

### 2.6 REST API Layer (1–2 days)
1. Ktor server with Netty engine
2. Endpoints:
   - `POST /api/upload` — multipart file upload (accepts CSV, XLS, XLSX)
     - Request: multipart form data with `file` part + optional JSON config
     - Config fields: `gatewayUrl`, `tagProvider`, `basePath`, `dryRun`, `onError` (continue|stop), `onDuplicate` (skip|update|fail), `encoding`
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
    val address: String,                        // Required: OPC item path or device address
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

enum class ErrorStrategy { CONTINUE, STOP }
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
    val status: String,                         // "created", "updated", "skipped", "failed"
    val error: String? = null
)

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

**Depends on chosen Ignition approach**:
- If A or C: OkHttp 5.x (HTTP client for outbound calls to Ignition)
- If B: Ignition Module SDK (adds module packaging, signing, `GatewayModuleHook`)
- If C: Requires WebDev module installed on Ignition Gateway

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
        token = ${?IGNITION_API_TOKEN}
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
