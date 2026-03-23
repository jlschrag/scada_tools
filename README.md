# Ignition SCADA Tag Bulk Uploader

> **Status**: ✅ **Phase 1 (POC) COMPLETE** - Python FastAPI Implementation  
> **Tech Stack**: Python 3.11+ | FastAPI | httpx | Pydantic  
> **Integration**: Ignition Gateway REST API (`POST /data/api/v1/tags/import`)

A REST API service for bulk uploading tags to Inductive Automation's Ignition SCADA platform from spreadsheets (CSV, Excel).

## 📋 Project Status

- ✅ **Phase 0**: Research & Architecture Decision (COMPLETE)
- ✅ **Phase 1**: Proof of Concept (COMPLETE) - **Security hardened, code reviewed**
- 🚧 **Phase 2**: Full Implementation (Planned)

**Latest Update**: All Phase 1 code review feedback addressed. See [REVIEW_FEEDBACK_APPLIED.md](REVIEW_FEEDBACK_APPLIED.md) for details.

## 🚀 Quick Start (Phase 1 POC)

### Prerequisites

- Python 3.11 or higher
- Docker (for running Ignition Gateway)
- Git

### 1. Clone & Setup

```bash
# Clone the repository
cd scada_tools

# Run the quick start script (Linux/macOS)
./run.sh
# ⚠️ This will create .env with default credentials (admin/password)
# Edit .env to set proper credentials before production use!

# Or manually:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set IGNITION_USERNAME and IGNITION_PASSWORD
```

### 2. Start Ignition Gateway

```bash
# Start Ignition container
docker-compose up -d

# Wait ~60 seconds for initialization
# Gateway will be available at http://localhost:8088
# Default credentials: admin / password
```

### 3. Run the API

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# API available at: http://localhost:8080
# Interactive docs: http://localhost:8080/docs
```

### 4. Test the API

```bash
# Check health
curl http://localhost:8080/api/health

# Upload a test file (creates a POC tag)
echo "test" > test.csv
curl -X POST http://localhost:8080/api/upload -F "file=@test.csv"
```

## 📚 Documentation

- **[PHASE1_README.md](PHASE1_README.md)** - Complete Phase 1 documentation, API reference, and findings
- **[PLAN.md](PLAN.md)** - Full implementation roadmap and architecture decisions
- **[CONTEXT.md](CONTEXT.md)** - Research notes and technical analysis

## 🎯 Phase 1 Features

✅ **REST API Skeleton**
- `GET /api/health` - Service status and Ignition connectivity
- `POST /api/upload` - File upload (creates test tag for POC)

✅ **Ignition Integration**
- API token generation (`POST /data/api/v1/api-token/generate`)
- Tag creation via import endpoint (`POST /data/api/v1/tags/import`)
- QualityCode response parsing
- Bearer token authentication

✅ **Documentation**
- Request/response formats documented
- Authentication method confirmed
- Tag JSON format captured

## 🔧 Configuration

**⚠️ IMPORTANT**: Credentials are **required** - the application will not start without them.

Create a `.env` file (or copy `.env.example`):

```bash
# Ignition Gateway (REQUIRED)
IGNITION_GATEWAY_URL=http://localhost:8088
IGNITION_USERNAME=admin          # CHANGE THIS!
IGNITION_PASSWORD=password       # CHANGE THIS!
IGNITION_VERIFY_SSL=False

# API Server
API_HOST=0.0.0.0
API_PORT=8080
LOG_LEVEL=INFO

# Tag Provider
TAG_PROVIDER=default
OPC_SERVER_NAME=Ignition OPC UA Server

# Upload Settings
MAX_FILE_SIZE=10485760
ALLOWED_FILE_EXTENSIONS=[".csv",".xlsx",".xls"]
```

**Security Notes:**
- Username and password have no defaults in the code
- The app will fail fast if credentials are not provided
- Never commit `.env` to version control (it's in `.gitignore`)

## 🏗️ Architecture

### Technology Stack

**Backend:**
- FastAPI - Modern Python web framework
- Uvicorn - ASGI server
- httpx - Async HTTP client for Ignition API
- Pydantic - Data validation and settings

**Integration:**
- Ignition Gateway REST API (Approach A from research)
- API Token authentication
- JSON tag import format

### Project Structure

```
scada_tools/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── models.py            # Pydantic models
│   └── ignition_client.py   # Ignition Gateway client
├── tests/                   # Test suite (Phase 2)
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Modern Python project config
├── docker-compose.yml      # Ignition test environment
└── PHASE1_README.md        # Phase 1 documentation
```

## 🧪 Testing

### Automated Unit Tests

```bash
# Run pytest suite (15 unit tests)
pytest tests/ -v

# Tests cover:
# - Settings/configuration validation
# - Pydantic model serialization
# - Required credential enforcement
```

### Manual Integration Test

```bash
# Test Ignition integration directly (requires Ignition running)
python test_phase1.py

# Tests:
# 1. Ignition Gateway connectivity
# 2. API token generation
# 3. Tag creation via import endpoint
```

### API Testing

```bash
# Interactive API documentation
open http://localhost:8080/docs

# Health check
curl http://localhost:8080/api/health

# Upload test file
curl -X POST http://localhost:8080/api/upload -F "file=@test.csv"
```

## 📖 Key Findings (Phase 1)

### Authentication
- ✅ API token generation works via `POST /data/api/v1/api-token/generate`
- ✅ Bearer token auth: `Authorization: Bearer <api-key>`
- ✅ Token includes `key` (use in requests) and `hash` (server reference)

### Tag Import
- ✅ Endpoint: `POST /data/api/v1/tags/import?provider=default&type=json&collisionPolicy=Overwrite`
- ✅ Body: JSON-encoded tag definition as `application/octet-stream`
- ✅ Response: Empty array = success, otherwise `QualityCode[]` with errors
- ✅ Collision policies: Abort, Overwrite, Rename, Ignore, MergeOverwrite

### Tag Format
- ✅ Minimum fields: `name`, `tagType`, `dataType`, `valueSource`
- ✅ For OPC tags: `opcServer`, `opcItemPath` required
- ✅ Must wrap in `{"tags": [...]}`

## 🔮 Phase 2 Roadmap

Phase 2 will implement:

1. **Spreadsheet Parsing** - CSV, Excel (XLSX, XLS)
2. **Validation** - Tag names, data types, required fields
3. **Bulk Import** - Process hundreds/thousands of tags
4. **Error Handling** - Per-tag error reporting
5. **Configuration** - Dry-run, collision policy, base path
6. **Testing** - Unit tests, integration tests, sample files

See [PLAN.md](PLAN.md) for detailed Phase 2 timeline.

## 🐳 Docker Reference

```bash
# Pull Ignition image
docker pull inductiveautomation/ignition:latest

# Run Ignition container
docker run -d --name ignition \
  -p 8088:8088 -p 8043:8043 \
  -e ACCEPT_IGNITION_EULA=Y \
  -e GATEWAY_ADMIN_USERNAME=admin \
  -e GATEWAY_ADMIN_PASSWORD=password \
  -e IGNITION_EDITION=standard \
  inductiveautomation/ignition:latest

# Or use docker-compose
docker-compose up -d
docker-compose logs -f ignition
```

## 🤝 Contributing

This is a Phase 1 POC. Contributions welcome for Phase 2 implementation!

## 📄 License

[License information to be added]

## 🔗 Resources

- [Ignition Platform](https://inductiveautomation.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Ignition Docker Hub](https://hub.docker.com/r/inductiveautomation/ignition)
