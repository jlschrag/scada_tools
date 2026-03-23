# Developer Guide - Phase 1 POC

Quick reference for developers working on the Ignition Tag Bulk Uploader.

## 🚀 Quick Start

```bash
# 1. Setup Python environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env if needed

# 3. Start Ignition Gateway (Docker)
docker-compose up -d

# 4. Wait for Ignition to initialize (~60 seconds)
docker-compose logs -f ignition

# 5. Test Ignition integration
python test_phase1.py

# 6. Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

# 7. Open interactive API docs
open http://localhost:8080/docs
```

## 📁 Project Structure

```
scada_tools/
├── app/                        # Main application package
│   ├── __init__.py            # Package initialization (version)
│   ├── main.py                # FastAPI app & route handlers
│   ├── config.py              # Settings (env vars → Pydantic)
│   ├── models.py              # Request/response models
│   └── ignition_client.py     # Ignition Gateway API client
│
├── tests/                      # Test suite (Phase 2)
│   └── __init__.py
│
├── examples/                   # Sample files
│   ├── sample_tags.csv        # Example CSV for Phase 2
│   └── README.md
│
├── requirements.txt           # Python dependencies
├── pyproject.toml            # Modern Python project config
├── docker-compose.yml        # Ignition test container
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
│
├── run.sh                    # Quick start script
├── test_phase1.py            # Manual integration test
│
├── README.md                 # Main project README
├── PHASE1_README.md          # Phase 1 documentation
├── DEVELOPER_GUIDE.md        # This file
├── CHANGELOG.md              # Version history
├── PLAN.md                   # Implementation roadmap
└── CONTEXT.md                # Research notes
```

## 🔧 Core Components

### 1. Configuration (`app/config.py`)

Uses `pydantic-settings` for environment-based config:

```python
from app.config import settings

# Access settings
print(settings.ignition_gateway_url)
print(settings.tag_provider)
```

**Environment Variables:**
- `IGNITION_GATEWAY_URL` - Gateway URL (default: http://localhost:8088)
- `IGNITION_USERNAME` - Admin username (default: admin)
- `IGNITION_PASSWORD` - Admin password (default: password)
- `IGNITION_VERIFY_SSL` - Verify SSL certs (default: False)
- `TAG_PROVIDER` - Tag provider name (default: default)
- `API_PORT` - API server port (default: 8080)

### 2. Ignition Client (`app/ignition_client.py`)

Singleton client for Ignition Gateway REST API:

```python
from app.ignition_client import ignition_client

# Check connectivity
connected = await ignition_client.check_connectivity()

# Generate API token
token = await ignition_client.generate_api_token()

# Create a tag
quality_codes = await ignition_client.create_minimal_tag(
    tag_name="MyTag",
    tag_path="Folder/SubFolder"
)

# Empty quality_codes = success
if not quality_codes:
    print("Tag created successfully!")
```

**Key Methods:**
- `check_connectivity()` → `bool`
- `generate_api_token()` → `ApiTokenResponse`
- `export_tag(tag_path, provider)` → `Dict[str, Any]`
- `import_tag(tag_json, provider, collision_policy)` → `List[QualityCode]`
- `create_minimal_tag(tag_name, tag_path)` → `List[QualityCode]`

### 3. FastAPI Application (`app/main.py`)

**Endpoints:**

```python
# Health check
GET /api/health
→ HealthResponse

# Upload file (POC: creates test tag)
POST /api/upload
Form-data: file=<file>
→ UploadResponse

# Root info
GET /
→ JSON with API info
```

**Running:**
```bash
# Development (auto-reload)
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```

### 4. Models (`app/models.py`)

Pydantic models for type safety:

```python
from app.models import (
    HealthResponse,
    UploadResponse,
    TagImportResult,
    ApiTokenResponse,
    QualityCode
)
```

## 🧪 Testing

### Manual Integration Test

```bash
# Run all tests
python test_phase1.py

# Tests:
# 1. Ignition connectivity
# 2. API token generation
# 3. Tag creation
```

### API Testing (curl)

```bash
# Health check
curl http://localhost:8080/api/health | jq

# Upload file
echo "test" > test.csv
curl -X POST http://localhost:8080/api/upload \
  -F "file=@test.csv" | jq
```

### API Testing (httpie)

```bash
# Install httpie: pip install httpie

# Health check
http GET localhost:8080/api/health

# Upload
http --form POST localhost:8080/api/upload file@test.csv
```

### Interactive API Docs

FastAPI provides automatic API documentation:

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## 🐳 Docker Commands

### Ignition Gateway

```bash
# Start container
docker-compose up -d

# View logs
docker-compose logs -f ignition

# Check status
docker-compose ps

# Stop container
docker-compose stop

# Remove container & volumes
docker-compose down -v

# Restart container
docker-compose restart ignition
```

### Direct Docker (without compose)

```bash
# Pull image
docker pull inductiveautomation/ignition:latest

# Run container
docker run -d \
  --name ignition \
  -p 8088:8088 \
  -p 8043:8043 \
  -e ACCEPT_IGNITION_EULA=Y \
  -e GATEWAY_ADMIN_USERNAME=admin \
  -e GATEWAY_ADMIN_PASSWORD=password \
  -e IGNITION_EDITION=standard \
  inductiveautomation/ignition:latest

# Check logs
docker logs -f ignition

# Stop
docker stop ignition

# Remove
docker rm ignition
```

## 🔍 Debugging

### Enable Debug Logging

Add to `app/main.py`:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

### Test Ignition Connectivity

```bash
# Check gateway info
curl http://localhost:8088/system/gwinfo

# Should return gateway metadata
```

### Test API Token Generation

```bash
curl -X POST http://localhost:8088/data/api/v1/api-token/generate \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}' | jq
```

### SSL Certificate Issues

If you get SSL errors:

1. **Disable verification** (development only):
   ```bash
   echo "IGNITION_VERIFY_SSL=False" >> .env
   ```

2. **Use HTTP instead of HTTPS**:
   ```bash
   echo "IGNITION_GATEWAY_URL=http://localhost:8088" >> .env
   ```

## 📊 Ignition Gateway REST API Reference

### Base URL

- HTTP: `http://localhost:8088`
- HTTPS: `https://localhost:8043`

### Authentication Flow

1. **Generate Token:**
   ```
   POST /data/api/v1/api-token/generate
   {"username": "admin", "password": "password"}
   → {"key": "abc...", "hash": "xyz..."}
   ```

2. **Use Token:**
   ```
   Authorization: Bearer <key>
   ```

### Key Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/data/api/v1/api-token/generate` | Generate API token |
| GET | `/data/api/v1/tags/export` | Export tags (JSON/XML/CSV) |
| POST | `/data/api/v1/tags/import` | Import tags |
| GET | `/system/gwinfo` | Gateway information |

### Tag Import Query Params

- `provider` - Tag provider name (e.g., "default")
- `type` - Import format: "json", "xml", "csv"
- `collisionPolicy` - Abort, Overwrite, Rename, Ignore, MergeOverwrite
- `path` - Optional base path

### Tag JSON Format

```json
{
  "tags": [
    {
      "name": "TagName",
      "path": "Folder/SubFolder",
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

## 🛠️ Common Tasks

### Add a New Endpoint

1. Define route in `app/main.py`:
   ```python
   @app.get("/api/new-endpoint")
   async def new_endpoint():
       return {"message": "Hello"}
   ```

2. Add response model in `app/models.py`:
   ```python
   class NewEndpointResponse(BaseModel):
       message: str
   ```

3. Update route:
   ```python
   @app.get("/api/new-endpoint", response_model=NewEndpointResponse)
   async def new_endpoint():
       return NewEndpointResponse(message="Hello")
   ```

### Add a New Configuration Option

1. Add to `app/config.py`:
   ```python
   class Settings(BaseSettings):
       new_option: str = "default_value"
   ```

2. Add to `.env.example`:
   ```
   NEW_OPTION=default_value
   ```

3. Use in code:
   ```python
   from app.config import settings
   print(settings.new_option)
   ```

### Add a New Ignition Client Method

1. Add to `app/ignition_client.py`:
   ```python
   async def new_method(self, param: str) -> Dict[str, Any]:
       url = f"{self.base_url}/endpoint"
       async with httpx.AsyncClient(verify=self.verify_ssl) as client:
           response = await client.get(url, headers={
               "Authorization": f"Bearer {self.api_token}"
           })
           response.raise_for_status()
           return response.json()
   ```

2. Use it:
   ```python
   result = await ignition_client.new_method("test")
   ```

## 📝 Code Style

### Python Style Guide

- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

### Format Code

```bash
# Install dev dependencies
pip install black ruff

# Format code
black app/ tests/

# Lint code
ruff app/ tests/
```

### Type Checking

```bash
# Install mypy
pip install mypy

# Check types
mypy app/
```

## 🔐 Security Notes

### Phase 1 (Development)

- SSL verification disabled by default
- Credentials in environment variables
- No authentication on API endpoints
- Suitable for local testing only

### Phase 2 (Production Considerations)

- Enable SSL verification
- Use secrets management (HashiCorp Vault, AWS Secrets Manager)
- Add API key authentication
- Implement rate limiting
- Add CORS configuration
- Use HTTPS for API

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [httpx Documentation](https://www.python-httpx.org/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Ignition User Manual](https://docs.inductiveautomation.com/)

## 🤝 Contributing

### Before Submitting PR

1. Format code: `black app/ tests/`
2. Lint code: `ruff app/ tests/`
3. Run tests: `pytest` (Phase 2)
4. Update CHANGELOG.md
5. Update documentation if needed

### Commit Message Format

```
type(scope): description

[optional body]

[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(api): add tag validation endpoint`
- `fix(client): handle SSL certificate errors`
- `docs(readme): update installation instructions`

## ❓ FAQ

**Q: Why Python instead of Kotlin?**  
A: User requested Python implementation for Phase 1. FastAPI provides similar developer experience to Ktor with async/await support.

**Q: Why disable SSL verification?**  
A: Ignition often uses self-signed certificates in development. For production, use proper SSL certificates and enable verification.

**Q: How do I reset the Ignition Gateway?**  
A: `docker-compose down -v` to remove volumes, then `docker-compose up -d` to start fresh.

**Q: Why does tag creation return empty array?**  
A: Empty array means success! Non-empty array contains QualityCode errors.

**Q: How do I change the Ignition admin password?**  
A: Edit `docker-compose.yml` → `GATEWAY_ADMIN_PASSWORD` environment variable, then recreate container.

## 🚧 Known Issues (Phase 1)

1. **File upload doesn't parse content** - Phase 1 creates hardcoded test tag. Parsing implemented in Phase 2.
2. **No tag validation** - Any tag structure is sent to Ignition. Validation in Phase 2.
3. **Single tag creation only** - Bulk import in Phase 2.
4. **No error granularity** - Don't know which specific tag failed if batch has issues. Phase 1 goal is to test the endpoint, not production use.

## 📞 Support

For issues or questions:
1. Check PHASE1_README.md
2. Check PLAN.md for roadmap
3. Check CONTEXT.md for technical details
4. Review Ignition logs: `docker-compose logs ignition`
5. Review API logs in terminal where uvicorn is running
