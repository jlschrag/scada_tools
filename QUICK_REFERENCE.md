# Quick Reference - Phase 1 POC

Essential commands and information for the Ignition Tag Bulk Uploader.

## 🚀 One-Line Setup & Run

```bash
# Clone, setup, and run (assumes Docker is running)
git clone <repo> && cd scada_tools && ./run.sh
```

## 📦 Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
```

## 🐳 Ignition Gateway

```bash
# Start Ignition (Docker Compose)
docker-compose up -d

# View logs
docker-compose logs -f ignition

# Check status
docker-compose ps

# Stop
docker-compose stop

# Remove (with data)
docker-compose down -v
```

## 🖥️ Run API Server

```bash
# Development mode (auto-reload)
uvicorn app.main:app --reload

# Or use the helper script
./run.sh

# Or with Python module
python -m app.main
```

**Server URLs:**
- API: http://localhost:8080
- Docs: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## 🧪 Testing

```bash
# Run manual test suite
python test_phase1.py

# Test health endpoint
curl http://localhost:8080/api/health | jq

# Test upload endpoint
echo "test" > test.csv
curl -X POST http://localhost:8080/api/upload -F "file=@test.csv" | jq
```

## 📡 API Endpoints

### Health Check
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

### Upload File
```bash
curl -X POST http://localhost:8080/api/upload \
  -F "file=@examples/sample_tags.csv" | jq
```

**Response:**
```json
{
  "status": "success",
  "message": "Tag created successfully",
  "tags_processed": 1,
  "results": [...]
}
```

## 🔧 Environment Variables

Create `.env` file:

```bash
# Ignition Gateway
IGNITION_GATEWAY_URL=http://localhost:8088
IGNITION_USERNAME=admin
IGNITION_PASSWORD=password
IGNITION_VERIFY_SSL=False

# API Server
API_PORT=8080
TAG_PROVIDER=default
```

## 🐛 Troubleshooting

### Ignition Not Reachable
```bash
# Check container
docker-compose ps

# View logs
docker-compose logs ignition

# Restart
docker-compose restart ignition

# Test connectivity
curl http://localhost:8088/system/gwinfo
```

### API Won't Start
```bash
# Check if port is in use
lsof -i :8080

# Use different port
API_PORT=8081 uvicorn app.main:app --reload --port 8081
```

### Import Errors
```bash
# Verify virtual environment is activated
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### SSL Certificate Errors
```bash
# Disable SSL verification (dev only)
echo "IGNITION_VERIFY_SSL=False" >> .env

# Or use HTTP instead of HTTPS
echo "IGNITION_GATEWAY_URL=http://localhost:8088" >> .env
```

## 📁 Project Structure

```
scada_tools/
├── app/                    # FastAPI application
│   ├── main.py            # API endpoints
│   ├── config.py          # Configuration
│   ├── models.py          # Data models
│   └── ignition_client.py # Ignition integration
├── tests/                 # Tests
├── examples/              # Sample files
│   └── sample_tags.csv
├── requirements.txt       # Dependencies
├── .env                   # Configuration (create from .env.example)
└── docker-compose.yml     # Ignition container
```

## 🔑 Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | API endpoints |
| `app/ignition_client.py` | Ignition Gateway client |
| `app/config.py` | Environment configuration |
| `test_phase1.py` | Manual integration tests |
| `docker-compose.yml` | Ignition test environment |
| `PHASE1_README.md` | Complete documentation |

## 📚 Documentation

- **Quick Start:** README.md
- **Complete Guide:** PHASE1_README.md
- **Developer Reference:** DEVELOPER_GUIDE.md
- **Roadmap:** PLAN.md
- **Research:** CONTEXT.md

## 🎯 Phase 1 Capabilities

✅ **What Works:**
- REST API with file upload
- Health check endpoint
- Ignition API token generation
- Create one tag programmatically
- Bearer token authentication
- QualityCode response parsing

❌ **Not Yet Implemented (Phase 2):**
- Spreadsheet parsing
- Bulk tag import
- Tag validation
- Per-tag error reporting
- Dry-run mode
- Collision policy configuration

## 🔗 Important URLs

### API Server (when running)
- Main API: http://localhost:8080
- Interactive Docs: http://localhost:8080/docs
- Alternative Docs: http://localhost:8080/redoc
- OpenAPI JSON: http://localhost:8080/openapi.json

### Ignition Gateway (when running)
- HTTP: http://localhost:8088
- HTTPS: https://localhost:8043
- System Info: http://localhost:8088/system/gwinfo

## 💡 Common Tasks

### Add Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Change API Port
```bash
# In .env
API_PORT=8081

# Or via command line
uvicorn app.main:app --port 8081
```

### Reset Ignition
```bash
docker-compose down -v  # Remove volumes
docker-compose up -d     # Fresh start
```

### Format Code
```bash
pip install black ruff
black app/ tests/
ruff app/ tests/
```

## 📞 Getting Help

1. Check **PHASE1_README.md** for complete documentation
2. Check **DEVELOPER_GUIDE.md** for developer reference
3. Review logs: `docker-compose logs ignition`
4. Check API logs in terminal where uvicorn is running
5. Test with `python test_phase1.py`

## ⚡ Quick Commands Summary

```bash
# Setup
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Start Ignition
docker-compose up -d

# Run API
uvicorn app.main:app --reload

# Test
python test_phase1.py
curl http://localhost:8080/api/health
```

---

**Phase 1 POC Complete ✅**

See PHASE1_README.md for full documentation.
