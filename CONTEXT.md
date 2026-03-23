# Implementation Context & Reference Guide

## ✅ RESOLVED: Tag Creation Mechanism Confirmed

**Date**: 2026-03-23
**Status**: RESOLVED — Tag import endpoint confirmed via OpenAPI spec analysis

### Findings from OpenAPI Spec (`ignition_openapi_spec_1_0_0.json`)

**Q1: Does the OpenAPI have a tag creation endpoint?**
- **YES** — via `POST /data/api/v1/tags/import`. There is NO individual tag CRUD endpoint (no `POST /api/v1/tags`), but the **import endpoint IS the creation mechanism**. It accepts binary payloads of tag definitions in JSON, XML, or CSV format.

**Q2: What is the exact format the import endpoint expects?**
- Request body: `application/octet-stream` — raw bytes of an export file
- Required query params: `provider` (string), `type` (`json`|`xml`|`csv`), `collisionPolicy` (`Abort`|`Overwrite`|`Rename`|`Ignore`|`MergeOverwrite`)
- Optional query param: `path` (target folder path)
- The export endpoint (`GET /data/api/v1/tags/export`) produces `json` and `xml` (NOT csv)
- **Recommended strategy**: Generate **Ignition JSON export format** for the import payload (not CSV), since JSON is the format that both export and import share and is the most reliable

**Q3: Authentication method?**
- Ignition uses **API Tokens** (not Bearer/OAuth for the data API)
- `POST /data/api/v1/api-token/generate` returns a `{ key, hash }` pair
- The `key` is "the credential that the client will include with each request for authentication purposes"
- The `hash` is sent to Ignition when creating the API token resource (via `/data/api/v1/resources/ignition/api-token`)
- **The exact HTTP header name for sending the key is not documented in the spec** — must be verified empirically in Phase 1

**Q4: Collision policies?**
- Fully documented: `Abort`, `Overwrite`, `Rename`, `Ignore`, `MergeOverwrite`
- Maps to `DuplicateStrategy`: `SKIP` → `Ignore`, `UPDATE` → `MergeOverwrite`, `FAIL` → `Abort`

**Q5: Response format?**
- Success (200): Returns `[]` (empty array) if all imports succeeded
- Returns array of `{ level, userCode, diagnosticMessage }` quality code objects for any tags that failed
- No other HTTP status codes documented for the import endpoint

**Q6: Rate limiting / payload size limits?**
- **Not documented in the OpenAPI spec** — must be tested in Phase 1

### Approach Decision

| # | Approach | Status | Confidence |
|---|----------|--------|------------|
| A | REST API (Tag Import endpoint) | ✅ **SELECTED** | HIGH ✅ |
| B | Module SDK (`TagManager`) | ❌ Not needed | N/A |
| C | Scripting Bridge (WebDev) | ❌ Not needed | N/A |

### Phase 1 Verification Tasks (Remaining Unknowns)

These items need empirical testing against a live Ignition instance:

1. **Exact auth header format** — how the API token key is sent in HTTP requests
2. **Ignition JSON tag export format** — export sample tags and document the structure
3. **CSV import column format** — what columns/headers does Ignition expect for CSV tag import?
4. **Error response codes** — test 401, 400, etc. to document HTTP-level errors
5. **Payload size limits** — test with 100, 1000, 10000 tags
6. **Ignition data types** — export tags of various types to capture the exact type identifiers
7. **OPC address format in JSON** — how `opcItemPath` and `opcServer` are represented in the export format

---

## Research Links

| Resource | URL | Status |
|----------|-----|--------|
| Ignition 8.3 OpenAPI docs | https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi | ✅ Reviewed — spec analyzed |
| OpenAPI spec (local) | `./ignition_openapi_spec_1_0_0.json` | ✅ Analyzed — tag import/export endpoints confirmed |
| `system.tag.configure()` | https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-tag/system-tag-configure | ⬜ Not needed (Approach A selected) |
| Module SDK guide | https://www.docs.inductiveautomation.com/docs/8.3/developers/module-development | ⬜ Not needed (Approach A selected) |
| Module SDK examples | https://github.com/inductiveautomation/ignition-module-examples | ⬜ Not needed (Approach A selected) |
| Tag configuration properties | https://www.docs.inductiveautomation.com/docs/8.3/platform/tags | ⬜ Review in Phase 1 |
| WebDev module | https://www.docs.inductiveautomation.com/docs/8.3/platform/modules/web-dev | ⬜ Not needed (Approach A selected) |
| Ignition data types | https://www.docs.inductiveautomation.com/docs/8.3/platform/tags/tag-properties | ⬜ Review in Phase 1 |

---

## Project Meta
- **Name**: Ignition SCADA Tag Bulk Uploader
- **Architecture**: REST API service (Ktor + Netty)
- **Language**: Kotlin
- **Build System**: Gradle (Kotlin DSL)
- **Target**: Ignition 8.3+
- **JVM Version**: Java 11+
- **Deployment**: Containerized (Docker)
- **Created**: 2026-03-23

### Decisions Made
- ✅ User-facing interface: **REST API** (not CLI)
- ✅ Framework: **Ktor** (Kotlin-native, lightweight)
- ✅ Deployment: **Docker container**
- ✅ Ignition integration mechanism: **Gateway REST API — `POST /data/api/v1/tags/import`** (Approach A)

## Key Dependencies (To Be Added)

### Spreadsheet Parsing
```gradle
// Apache POI for Excel (.xlsx, .xls)
implementation 'org.apache.poi:poi:5.2.3'
implementation 'org.apache.poi:poi-ooxml:5.2.3'

// OpenCSV for CSV parsing
implementation 'com.opencsv:opencsv:5.8'
```

### REST API Server (Ktor)
```gradle
// Ktor Server
implementation 'io.ktor:ktor-server-core'
implementation 'io.ktor:ktor-server-netty'
implementation 'io.ktor:ktor-server-content-negotiation'
implementation 'io.ktor:ktor-serialization-jackson'
implementation 'io.ktor:ktor-server-cors'
implementation 'io.ktor:ktor-server-call-logging'

// Ktor Test Client
testImplementation 'io.ktor:ktor-server-test-host'
testImplementation 'io.ktor:ktor-client-content-negotiation'
```

### HTTP Client (outbound calls to Ignition)
```gradle
// OkHttp for calling Ignition Gateway
implementation 'com.squareup.okhttp3:okhttp:5.x'
```

### Logging
```gradle
implementation 'org.slf4j:slf4j-api:2.0.x'
implementation 'ch.qos.logback:logback-classic:1.4.x'
```

### JSON Serialization
```gradle
implementation 'com.fasterxml.jackson.module:jackson-module-kotlin:2.x'
```

### Testing
```gradle
testImplementation 'org.junit.jupiter:junit-jupiter:5.10.0'
testImplementation 'io.mockk:mockk:1.13.5'  // MockK — single Kotlin-idiomatic mocking framework
```

### Configuration
```gradle
// HOCON config (used by Ktor natively via application.conf)
// No additional dependency needed — Ktor includes it

// YAML support for optional config files
implementation 'com.fasterxml.jackson.dataformat:jackson-dataformat-yaml:2.x'
```

---

## Ignition API Research Checklist

### Documentation To Review
- [x] https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi — Analyzed via local spec file
- [x] OpenAPI v3 schema specification — `ignition_openapi_spec_1_0_0.json` analyzed
- [x] Authentication methods documentation — API Token mechanism confirmed
- [ ] Rate limiting / throttling info — Not in spec, test in Phase 1
- [x] Error response formats — QualityCode array documented
- [x] Tag creation endpoint details — `POST /data/api/v1/tags/import` confirmed

### Key Endpoints (✅ CONFIRMED from OpenAPI spec)
```
POST /data/api/v1/tags/import          — Tag creation (bulk import)
  Query params: provider (required), type (required: json|xml|csv),
                collisionPolicy (required: Abort|Overwrite|Rename|Ignore|MergeOverwrite),
                path (optional)
  Body: application/octet-stream (tag export file bytes)
  Response: JSON array of QualityCode objects (empty = all good)

GET  /data/api/v1/tags/export          — Tag export (for format reference)
  Query params: provider (required), type (required: json|xml),
                path (optional), recursive (optional, default true),
                includeUdts (optional, default true)

POST /data/api/v1/api-token/generate   — Generate auth token (returns { key, hash })
PUT  /data/api/v1/resources/ignition/api-token — Create API token resource
GET  /data/api/v1/resources/find/ignition/api-token/{name} — Get token config
PUT  /data/api/v1/managed-tag-provider — Manage tag provider settings

Authentication: API Token (key from /api-token/generate, exact header TBD — Phase 1)
Request Format: application/octet-stream (import), JSON (token ops)
Response Format: JSON
Rate Limit: Not documented — test in Phase 1
Max Payload Size: Not documented — test in Phase 1
```

### Ignition Data Types Reference (FILL IN AFTER RESEARCH)
Likely types (confirm from docs):
- Boolean
- Integer
- Long
- Float
- Double
- String
- DateTime
- Array types (if supported)
- Custom types (if applicable)

**Mapping Strategy**:
1. User enters: "int" | "integer" | "Integer"
2. Normalize to: "Integer"
3. Validate against Ignition's type system
4. Send to API with proper format

### Tag Naming Rules (FILL IN AFTER RESEARCH)
- [ ] Maximum length
- [ ] Allowed characters (alphanumeric, underscores, hyphens, dots?)
- [ ] Forbidden characters
- [ ] Case sensitivity
- [ ] Namespace/path requirements (folder structure)
- [ ] Reserved names

### Address Format Requirements (FILL IN AFTER RESEARCH)
- [ ] OPC-UA address format (e.g., `opc.tcp://host:port/path`)
- [ ] Device specific (ModBus, Ethernet IP, etc.)
- [ ] Validation rules
- [ ] Examples from documentation

### Authentication (✅ CONFIRMED from OpenAPI spec)
```
Method: API Token (key/hash pair)
Token Generation: POST /data/api/v1/api-token/generate → { key, hash }
Token Registration: POST /data/api/v1/resources/ignition/api-token (send hash)
Header: TBD — exact header format not in OpenAPI spec (Phase 1 verification)
Expiration: Not documented — likely configured per-token
Security: HTTPS strongly recommended (spec warns key could be compromised over HTTP)
Token Config: secureChannelRequired (boolean), securityLevels (array)
```

### Error Codes (Partially confirmed from OpenAPI spec)
```
Import endpoint (/tags/import):
  200 OK: Returns List<QualityCode> — empty array = success, non-empty = per-tag errors
         QualityCode: { level: string, userCode: integer, diagnosticMessage: string }
  (Other HTTP status codes not documented for import — test empirically in Phase 1)

Token generation (/api-token/generate):
  200 OK: Returns { key, hash }
  403 Forbidden: Request does not have required write permissions
  500 Server Error: Server error during token generation

General (test in Phase 1):
  400 Bad Request: [TBD]
  401 Unauthorized: [TBD — likely invalid/missing API token]
  429 Too Many Requests: [TBD — rate limiting not documented]
```

---

## Spreadsheet Format Specification

### Required Columns
1. **name** (required)
   - Tag name in Ignition
   - Must follow Ignition naming rules
   
2. **address** (required)
   - Device/OPC address
   - Format depends on device type
   
3. **dataType** (required)
   - Ignition data type identifier
   - Case-insensitive input (will be normalized)

4. **description** (optional)
   - User-friendly description
   - Can be empty/blank

### Example Spreadsheet

#### CSV Format
```csv
name,address,dataType,description
Temperature_Zone1,opc.tcp://plc1:4840/Zone1/Temp,float,Main zone temperature sensor
Pressure_Zone1,opc.tcp://plc1:4840/Zone1/Pressure,float,Main zone pressure gauge
RunStatus,opc.tcp://plc1:4840/Status,bool,System running state
```

#### Excel Format
| name | address | dataType | description |
|------|---------|----------|-------------|
| Temperature_Zone1 | opc.tcp://plc1:4840/Zone1/Temp | float | Main zone temperature sensor |
| Pressure_Zone1 | opc.tcp://plc1:4840/Zone1/Pressure | float | Main zone pressure gauge |
| RunStatus | opc.tcp://plc1:4840/Status | bool | System running state |

### Validation Rules
- [ ] All required columns present
- [ ] No duplicate tag names
- [ ] Valid tag names per Ignition rules
- [ ] Valid data types
- [ ] Valid address formats
- [ ] No excessive whitespace

---

## Implementation Tracking

### Phase 1: Core Infrastructure
- [ ] Gradle project initialized
- [ ] Dependencies added to build.gradle.kts
- [ ] Package structure created
- [ ] Data models created (TagDefinition, ApiResponse, ValidationResult)
- [ ] Exception hierarchy defined
- [ ] Logging configured

### Phase 2: Spreadsheet Parsing
- [ ] Abstract SpreadsheetParser base class
- [ ] CSV parser implementation
- [ ] XLSX parser implementation
- [ ] XLS parser implementation
- [ ] Factory pattern implemented
- [ ] Header validation
- [ ] Unit tests for all formats

### Phase 3: Validation & Mapping
- [ ] TagValidator implementation
- [ ] DataTypeMapper implementation
- [ ] Data type constraint database
- [ ] Tag naming validation
- [ ] Address format validation
- [ ] Unit tests

### Phase 4: API Integration
- [ ] Research Ignition OpenAPI
- [ ] IgnitionApiClient implementation
- [ ] Authentication handling
- [ ] Retry logic
- [ ] Error mapping
- [ ] Integration tests with mock API

### Phase 5: Orchestrator
- [ ] TagUploader main class
- [ ] Workflow coordination
- [ ] Progress reporting
- [ ] Result aggregation
- [ ] Error recovery
- [ ] End-to-end tests

### Phase 6: REST API Layer
- [ ] Ktor server with Netty engine
- [ ] POST /api/upload endpoint (multipart file upload)
- [ ] GET /api/health endpoint
- [ ] GET /api/types endpoint
- [ ] Content negotiation (Jackson JSON)
- [ ] File size limits
- [ ] CORS configuration
- [ ] Request logging
- [ ] application.conf configuration

### Phase 7: Documentation & Polish
- [ ] README.md
- [ ] KDoc comments
- [ ] Usage examples
- [ ] Sample spreadsheets
- [ ] Test coverage report
- [ ] Security review

---

## Configuration & Credentials

### Environment Variables
```bash
IGNITION_GATEWAY_URL=https://ignition.example.com:8043
IGNITION_API_TOKEN=your_api_token_here
LOG_LEVEL=INFO
```

### Application Configuration (`application.conf` — HOCON)
```hocon
ktor {
    deployment {
        port = 8080
        port = ${?PORT}
    }
    application {
        modules = [ com.scada.taguploader.ApplicationKt.module ]
    }
}

ignition {
    gateway {
        url = "https://localhost:8043"
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

## Testing Strategy Details

### Sample Data
- **small.csv**: 5-10 tags (basic validation)
- **medium.xlsx**: 50-100 tags (format coverage)
- **large.csv**: 1000+ tags (performance testing)
- **invalid_names.csv**: Tags with invalid characters
- **invalid_types.csv**: Unknown data types
- **invalid_addresses.csv**: Malformed addresses
- **edge_cases.xlsx**: Empty descriptions, special characters, unicode

### REST API Tests (Ktor Test Client)
- Test `POST /api/upload` with sample CSV, XLSX, XLS files
- Test `GET /api/health` returns correct status
- Test `GET /api/types` returns data type list
- Test dry-run mode returns validation only
- Test error responses (bad file, missing fields, invalid types)
- Test file size limit enforcement

### Mock Ignition API
- Use WireMock or MockWebServer for unit tests
- Mock endpoints based on Phase 0 findings

### Performance Benchmarks (Target)
- CSV parsing: < 100ms for 1000 tags
- Validation: < 500ms for 1000 tags
- API creation: 10-100 tags/second (depends on network/server)
- File upload response: < 30s for 1000 tags

---

## Security Checklist

- [ ] API credentials never logged
- [ ] HTTPS enforced for production
- [ ] Input sanitization implemented
- [ ] File upload scanning (if applicable)
- [ ] Temporary file cleanup
- [ ] Secret rotation mechanism
- [ ] Audit logging for created tags
- [ ] Rate limiting honored

---

## Deployment

### Primary: Docker Container
- [ ] Create Dockerfile (JVM + fat JAR via Gradle Shadow)
- [ ] Create docker-compose.yml for local development
- [ ] Configure `application.conf` with env var overrides
- [ ] Health check endpoint for container orchestration
- [ ] Document Docker usage and deployment

### If Approach B (Module SDK)
- [ ] Package Ignition module as `.modl`
- [ ] Determine if REST API lives inside module or as separate service
- [ ] Module signing for production
- [ ] Document installation steps

---

## Documentation Structure

```
/docs/
├── README.md                 # Main documentation
├── INSTALLATION.md          # Setup instructions (Docker focus)
├── API.md                   # REST API endpoint documentation
├── openapi.yaml             # OpenAPI/Swagger spec for OUR API
├── EXAMPLES.md              # Usage examples (curl, Postman)
├── CONFIGURATION.md         # Config options (application.conf, env vars)
├── TROUBLESHOOTING.md       # Common issues
├── DEVELOPMENT.md           # Contributing guide
└── IGNITION_RESEARCH.md     # Phase 0 research findings
```

---

## Important Links & References

### Official Documentation
- Ignition OpenAPI: https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi
- Ignition Installation: https://www.inductiveautomation.com/ignition

### Libraries
- Apache POI: https://poi.apache.org/
- OpenCSV: https://opencsv.sourceforge.net/
- OkHttp: https://square.github.io/okhttp/
- Ktor Client: https://ktor.io/docs/client.html
- Kotlin Documentation: https://kotlinlang.org/docs/

### Tools
- Gradle: https://gradle.org/
- Kotlin: https://kotlinlang.org/

---

## Notes & Observations

### Pre-Implementation Research
- [ ] Confirm Ignition 8.3 supports programmatic tag creation via OpenAPI
- [ ] Verify Java 11+ compatibility
- [ ] Check if batch tag creation is supported
- [ ] Research typical tag naming conventions at client sites
- [ ] Confirm OPC-UA vs other protocol support

### Known Unknowns (Remaining for Phase 1)
1. ~~Exact OpenAPI endpoint for tag creation~~ ✅ `POST /data/api/v1/tags/import`
2. ~~Authentication mechanism~~ ✅ API Token (key/hash) — **exact HTTP header TBD**
3. Supported data types in Ignition 8.3 — export sample tags to capture type identifiers
4. Tag namespace/folder structure — `path` query param confirmed, format TBD
5. ~~Batch operation support~~ ✅ Import endpoint takes entire file (inherently batch)
6. ~~Error response format~~ ✅ `List<QualityCode>` with `{ level, userCode, diagnosticMessage }`
7. Rate limiting policies — not documented, test empirically
8. **NEW**: Exact Ignition JSON tag export structure (needed to construct import payloads)
9. **NEW**: CSV import column schema (if CSV format is desired)
10. **NEW**: Per-tag error granularity in QualityCode response

### Potential Challenges
1. Ignition API documentation may be incomplete
2. Different Ignition deployments may have different OPC drivers
3. Address format varies by device type
4. Network/firewall restrictions to Ignition gateway
5. API token expiration and refresh handling
6. Large file parsing performance (1000+ tags)

---

## Version History

### 2026-03-23 - Initial Planning
- Created PLAN.md with 7-phase implementation strategy
- Identified technology stack and dependencies
- Outlined data models and architecture
- Defined testing strategy and security considerations

---

## Update Instructions

When new information is learned during implementation:
1. Update the RESEARCH sections above
2. Log findings in this CONTEXT.md
3. Update PLAN.md if assumptions change
4. Keep dependency versions current
5. Record API endpoint discoveries
6. Document any deviations from plan

