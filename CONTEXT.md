# Implementation Context & Reference Guide

## ⚠️ CRITICAL BLOCKER: Tag Creation Mechanism Unverified

**Date**: 2026-03-23
**Status**: OPEN — Must be resolved before any implementation

The previous plan assumed Ignition 8.3 exposes a REST API endpoint (e.g., `POST /api/v1/tags`) for creating tags. **This has not been verified.** The reviewer flagged this as the #1 critical issue.

### What We Know

**About Ignition's OpenAPI (Gateway REST API)**:
- Ignition 8.x includes an OpenAPI specification at the Gateway level
- Documented at: https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi
- The spec is accessible at `https://<gateway>:8043/system/openapi.json`
- **Unknown**: Whether tag creation/configuration endpoints are included
- **Risk**: The OpenAPI has historically focused on system status, alarming, and project resources — NOT tag CRUD operations

**About `system.tag.configure()`**:
- This is Ignition's **documented scripting function** for programmatic tag creation
- Docs: https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-tag/system-tag-configure
- Runs in Ignition's Jython scripting environment (Gateway scope, client scope, or Designer scope)
- Supports creating, modifying, and deleting tags
- Accepts a base tag path and a list of tag configuration dictionaries
- **Key limitation**: Cannot be called directly from external code — needs a bridge (WebDev module, custom module, or manual script console)

**About the Ignition Module SDK**:
- Ignition modules are Java-based plugins installed on the Gateway
- The SDK provides `GatewayContext.getTagManager()` for programmatic tag operations
- Modules are packaged as `.modl` files and must be signed for production use
- Docs: https://www.docs.inductiveautomation.com/docs/8.3/developers/module-development
- Examples: https://github.com/inductiveautomation/ignition-module-examples
- **Trade-off**: Most powerful but most complex (module lifecycle, signing, installation)

### Three Candidate Approaches

| # | Approach | Pros | Cons | Confidence |
|---|----------|------|------|------------|
| A | REST API (OpenAPI) | Simple, standalone CLI | May not exist for tags | LOW ❓ |
| B | Module SDK (`TagManager`) | Full power, no external deps | Complex packaging, signing | HIGH ✅ |
| C | Scripting Bridge (WebDev + `system.tag.configure()`) | Well-documented, moderate complexity | Requires WebDev module on Gateway | MEDIUM ⚡ |

### Action Required

Complete **Phase 0** of the implementation plan before proceeding:
1. Inspect the actual OpenAPI spec on a live Ignition 8.3 instance
2. Review `system.tag.configure()` documentation for exact schema
3. Evaluate Module SDK if approaches A and C are insufficient
4. Make a binding architecture decision

---

## Research Links

| Resource | URL | Status |
|----------|-----|--------|
| Ignition 8.3 OpenAPI docs | https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi | ⬜ Not reviewed |
| `system.tag.configure()` | https://www.docs.inductiveautomation.com/docs/8.3/appendix/scripting-functions/system-tag/system-tag-configure | ⬜ Not reviewed |
| Module SDK guide | https://www.docs.inductiveautomation.com/docs/8.3/developers/module-development | ⬜ Not reviewed |
| Module SDK examples | https://github.com/inductiveautomation/ignition-module-examples | ⬜ Not reviewed |
| Tag configuration properties | https://www.docs.inductiveautomation.com/docs/8.3/platform/tags | ⬜ Not reviewed |
| WebDev module | https://www.docs.inductiveautomation.com/docs/8.3/platform/modules/web-dev | ⬜ Not reviewed |
| Ignition data types | https://www.docs.inductiveautomation.com/docs/8.3/platform/tags/tag-properties | ⬜ Not reviewed |

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
- ⬜ Ignition integration mechanism: **PENDING Phase 0**

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
- [ ] https://www.docs.inductiveautomation.com/docs/8.3/platform/gateway/openapi
- [ ] OpenAPI v3 schema specification (if available)
- [ ] Authentication methods documentation
- [ ] Rate limiting / throttling info
- [ ] Error response formats
- [ ] Tag creation endpoint details

### Key Endpoints (FILL IN AFTER RESEARCH)
```
⚠️ UNVERIFIED — These are placeholder assumptions, NOT confirmed endpoints:
[METHOD] /api/v[VERSION]/tags          ← MAY NOT EXIST
[METHOD] /api/v[VERSION]/tags/{tagId}  ← MAY NOT EXIST
Authentication: Bearer token / API Key / Basic Auth (UNVERIFIED)
Request Format: JSON (FILL IN SCHEMA)
Response Format: JSON (FILL IN SCHEMA)
Rate Limit: [TBD]
Max Payload Size: [TBD]
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

### Authentication (FILL IN AFTER RESEARCH)
```
Method: [Bearer Token / API Key / Basic Auth / OAuth]
Header: [FILL IN]
Token Generation: [HOW TO GET TOKEN]
Expiration: [IF APPLICABLE]
Refresh: [IF APPLICABLE]
Security: [HTTPS REQUIRED?]
```

### Error Codes (FILL IN AFTER RESEARCH)
```
400 Bad Request: [COMMON CAUSES]
401 Unauthorized: [COMMON CAUSES]
403 Forbidden: [COMMON CAUSES]
409 Conflict: [TAG EXISTS?]
429 Too Many Requests: [RATE LIMIT]
500 Server Error: [COMMON CAUSES]
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

### Known Unknowns (To Research)
1. Exact OpenAPI endpoint for tag creation
2. Authentication mechanism (Bearer? API Key? Basic?)
3. Supported data types in Ignition 8.3
4. Tag namespace/folder structure requirements
5. Batch operation support and limits
6. Error response format and codes
7. Rate limiting policies

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

