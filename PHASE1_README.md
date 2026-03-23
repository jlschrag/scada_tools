# Phase 1 POC Implementation - Python FastAPI

## Overview

This is the **Phase 1 Proof of Concept** implementation of the Ignition SCADA Tag Bulk Uploader using **Python with FastAPI** (instead of Kotlin/Ktor as originally planned).

## Phase 1 Goals ✅

The POC demonstrates:

1. ✅ **REST API Skeleton**
   - `POST /api/upload` - Accepts a file upload (currently creates a hardcoded test tag)
   - `GET /api/health` - Returns service status and Ignition connectivity

2. ✅ **Ignition Gateway Integration**
   - Generate API token via `POST /data/api/v1/api-token/generate`
   - Create ONE tag programmatically via `POST /data/api/v1/tags/import`
   - Parse QualityCode response (empty array = success)

3. ✅ **Authentication & Format Documentation**
   - API token generation confirmed
   - Tag import JSON format documented
   - Request/response formats logged

## Project Structure

```
scada_tools/
├── app/
│   ├── __init__.py           # Package initialization
│   ├── main.py               # FastAPI application & endpoints
│   ├── config.py             # Configuration management
│   ├── models.py             # Pydantic models
│   └── ignition_client.py    # Ignition Gateway REST API client
├── tests/                    # Tests (to be added in Phase 2)
├── requirements.txt          # Python dependencies
├── docker-compose.yml        # Ignition test container
├── .env.example              # Environment variables template
└── PHASE1_README.md          # This file
```

## Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **Uvicorn** - ASGI server for FastAPI
- **httpx** - Async HTTP client for Ignition Gateway API calls
- **Pydantic** - Data validation and settings management
- **Python 3.11+** - Programming language

## Setup & Installation

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your Ignition Gateway details
# For local Docker testing, defaults should work
```

### 3. Start Ignition Gateway (Docker)

```bash
# Start Ignition container
docker-compose up -d

# Wait for Ignition to start (60-90 seconds)
# Check status: docker-compose logs -f ignition

# Gateway will be available at:
# - HTTP: http://localhost:8088
# - HTTPS: https://localhost:8043
# - Default credentials: admin / password
```

### 4. Run the FastAPI Application

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# Or use Python directly
python -m app.main
```

The API will be available at:
- API: http://localhost:8080
- Interactive docs: http://localhost:8080/docs
- Alternative docs: http://localhost:8080/redoc

## API Endpoints

### GET /api/health

Check service status and Ignition connectivity.

**Request:**
```bash
curl http://localhost:8080/api/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "ignition_connected": true,
  "ignition_gateway": "http://localhost:8088"
}
```

### POST /api/upload

Upload a file and create a test tag (Phase 1 POC).

**Request:**
```bash
# Create a dummy test file
echo "test content" > test.csv

# Upload the file
curl -X POST http://localhost:8080/api/upload \
  -F "file=@test.csv"
```

**Response:**
```json
{
  "status": "success",
  "message": "Tag created successfully",
  "tags_processed": 1,
  "results": [
    {
      "success": true,
      "tag_path": "POC_Phase1/POC_Test_Tag",
      "message": "Tag created successfully",
      "quality_codes": []
    }
  ]
}
```

## Ignition Gateway REST API - Phase 1 Findings

### Authentication

The Ignition Gateway uses **API Token authentication**:

1. **Generate Token:**
   ```
   POST /data/api/v1/api-token/generate
   Content-Type: application/json
   
   {
     "username": "admin",
     "password": "password"
   }
   ```

2. **Response:**
   ```json
   {
     "key": "abc123...",
     "hash": "xyz789..."
   }
   ```

3. **Use Token in Requests:**
   ```
   Authorization: Bearer abc123...
   ```

### Tag Import Endpoint

**Endpoint:** `POST /data/api/v1/tags/import`

**Query Parameters:**
- `provider` - Tag provider name (default: "default")
- `type` - Import format: "json", "xml", or "csv"
- `collisionPolicy` - How to handle existing tags:
  - `Abort` - Stop if any tag exists
  - `Overwrite` - Replace existing tags
  - `Rename` - Rename new tags
  - `Ignore` - Skip existing tags
  - `MergeOverwrite` - Merge folders, overwrite conflicting tags

**Request Headers:**
```
Authorization: Bearer <api-token>
Content-Type: application/octet-stream
```

**Request Body:**
JSON-encoded tag definition (as bytes):
```json
{
  "tags": [
    {
      "name": "TagName",
      "path": "FolderPath",
      "tagType": "AtomicTag",
      "dataType": "Int4",
      "valueSource": "opc",
      "enabled": true,
      "opcServer": "Ignition OPC UA Server",
      "opcItemPath": "[device]path/to/tag",
      "documentation": "Tag description"
    }
  ]
}
```

**Response:**
Array of `QualityCode` objects:
```json
[]  // Empty array = success

// Or if errors:
[
  {
    "level": "ERROR",
    "userCode": 1001,
    "diagnosticMessage": "Tag already exists"
  }
]
```

### Tag Export Endpoint

**Endpoint:** `GET /data/api/v1/tags/export`

**Query Parameters:**
- `provider` - Tag provider name
- `type` - Export format: "json", "xml", or "csv"
- `path` - Tag path to export (optional, exports all if omitted)

**Use Case:**
Export existing tags to understand the exact JSON format required for imports.

## Testing Workflow

### 1. Start Ignition Gateway

```bash
docker-compose up -d
# Wait ~60 seconds for startup
docker-compose logs -f ignition  # Check logs
```

### 2. Verify Ignition is Ready

```bash
# Check gateway info endpoint
curl http://localhost:8088/system/gwinfo

# Should return gateway information
```

### 3. Start FastAPI Application

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

### 4. Test Health Endpoint

```bash
curl http://localhost:8080/api/health
# Should show ignition_connected: true
```

### 5. Test Tag Creation

```bash
# Create dummy file
echo "test" > test.csv

# Upload file (triggers tag creation)
curl -X POST http://localhost:8080/api/upload -F "file=@test.csv"

# Should return success response
```

### 6. Verify Tag in Ignition

1. Open Ignition Designer
2. Navigate to Tag Browser
3. Look for `POC_Phase1/POC_Test_Tag`
4. Tag should be visible with Int4 data type

## Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | 0.0.0.0 | API server host |
| `API_PORT` | 8080 | API server port |
| `API_RELOAD` | False | Enable auto-reload in dev mode |
| `IGNITION_GATEWAY_URL` | http://localhost:8088 | Ignition Gateway URL |
| `IGNITION_USERNAME` | admin | Gateway admin username |
| `IGNITION_PASSWORD` | password | Gateway admin password |
| `IGNITION_VERIFY_SSL` | False | Verify SSL certificates (disable for self-signed) |
| `TAG_PROVIDER` | default | Tag provider name |
| `MAX_FILE_SIZE` | 10485760 | Max upload file size (10MB) |

## Key Findings - Phase 1

### ✅ What Works

1. **API Token Generation**
   - Endpoint works as documented
   - Returns both `key` (for use) and `hash` (server-side reference)
   - Token can be used with `Authorization: Bearer <key>` header

2. **Tag Import Endpoint**
   - Accepts JSON-encoded tag definitions as `application/octet-stream`
   - Returns empty array on success
   - Returns `QualityCode` array with errors if import fails

3. **Tag JSON Format**
   - Must wrap tags in `{"tags": [...]}`
   - Minimum required fields: `name`, `tagType`, `dataType`, `valueSource`
   - For OPC tags: `opcServer` and `opcItemPath` required

4. **Authentication**
   - Bearer token authentication works
   - No need for basic auth after token is generated
   - Token persists for the client session

5. **SSL Verification**
   - Can be disabled for self-signed certificates (local dev)
   - Set `IGNITION_VERIFY_SSL=False` in environment

### ⚠️ To Investigate in Phase 2

1. **Tag Export Format**
   - Need to export an existing tag to see the complete JSON structure
   - This will reveal all available tag properties
   - Different tag types (Memory, OPC, Expression, etc.) may have different schemas

2. **Error Granularity**
   - Does each `QualityCode` map to a specific tag?
   - Or are errors aggregated at batch level?
   - Test with intentional failures to determine

3. **Batch Size Limits**
   - What's the maximum number of tags in a single import?
   - Need to test with large payloads (1000+ tags)
   - May need chunking strategy

4. **Collision Policy Behavior**
   - How does `Overwrite` vs `MergeOverwrite` differ?
   - Test with existing tags and folder structures

5. **Tag Data Types**
   - What are all the valid `dataType` values?
   - Map user-friendly names to Ignition type IDs
   - Document supported types

## Next Steps - Phase 2

Phase 1 POC is **complete**. The following features will be implemented in Phase 2:

1. **Spreadsheet Parsing**
   - CSV parser (using `csv` module)
   - Excel parser (using `openpyxl` or `pandas`)
   - Auto-detect file format
   - Extract tag definitions from rows

2. **Validation**
   - Tag name validation (valid characters, length)
   - Required fields check
   - Data type validation
   - Duplicate detection

3. **Bulk Import**
   - Process multiple tags from spreadsheet
   - Batch import strategy
   - Progress tracking
   - Detailed error reporting per tag

4. **Configuration**
   - Upload config (dry-run, collision policy, base path)
   - Tag defaults (OPC server, provider)
   - Error handling strategy (continue/stop)

5. **Testing**
   - Unit tests for all components
   - Integration tests with mock Ignition
   - Sample spreadsheets
   - End-to-end tests

## Troubleshooting

### Ignition Gateway Not Reachable

```bash
# Check if container is running
docker-compose ps

# Check logs
docker-compose logs ignition

# Restart container
docker-compose restart ignition

# Wait ~60 seconds, then test
curl http://localhost:8088/system/gwinfo
```

### API Token Generation Fails

- Verify username/password in `.env`
- Check Ignition Gateway is fully started
- Ensure gateway is accessible at configured URL
- Check for authentication errors in logs

### Tag Import Fails

- Check API token is valid (regenerate if needed)
- Verify tag JSON format matches Ignition export format
- Review QualityCode error messages in response
- Ensure tag provider exists (default: "default")

### SSL Certificate Errors

- Set `IGNITION_VERIFY_SSL=False` for self-signed certs
- For production, use valid SSL certificates
- Consider using HTTPS endpoint (port 8043) with proper certs

## Development Notes

### Code Structure

- **`app/main.py`** - FastAPI application, route handlers
- **`app/config.py`** - Environment-based configuration
- **`app/models.py`** - Pydantic models for validation
- **`app/ignition_client.py`** - Ignition Gateway API client

### Design Decisions

1. **Async HTTP Client (httpx)**
   - Compatible with FastAPI's async/await
   - Better performance for I/O-bound operations
   - Single client instance reused across requests

2. **Pydantic for Validation**
   - Type-safe configuration
   - Automatic environment variable loading
   - Request/response validation

3. **Bearer Token Auth**
   - More secure than basic auth
   - Token can be rotated
   - Follows API best practices

4. **SSL Verification Optional**
   - Disabled by default for local development
   - Can be enabled for production deployments
   - Documented in environment configuration

## License

See main project README for license information.

## Contact

For questions or issues, refer to the main project documentation.
