"""FastAPI application - Phase 1 POC"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.models import HealthResponse, UploadResponse, TagImportResult
from app.ignition_client import get_ignition_client
from app import __version__

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(f"Starting Ignition SCADA Tag Bulk Uploader v{__version__}")
    logger.info(f"Ignition Gateway URL: {settings.ignition_gateway_url}")
    yield
    # Shutdown
    logger.info("Shutting down, closing HTTP connections...")
    client = get_ignition_client()
    await client.close()
    logger.info("Shutdown complete")


app = FastAPI(
    title="Ignition SCADA Tag Bulk Uploader",
    description="REST API for bulk uploading tags to Ignition Gateway",
    version=__version__,
    lifespan=lifespan
)

# Add CORS middleware for browser-based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint - returns service status and Ignition connectivity.
    
    Phase 1 Goal: Returns service status
    """
    # Check if Ignition Gateway is reachable
    client = get_ignition_client()
    ignition_connected = await client.check_connectivity()
    
    return HealthResponse(
        status="healthy" if ignition_connected else "degraded",
        version=__version__,
        ignition_connected=ignition_connected,
        ignition_gateway=settings.ignition_gateway_url
    )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_tags(file: UploadFile = File(...)):
    """
    Upload endpoint - accepts a file and processes it.
    
    Phase 1 Goal: Accepts a hardcoded test file, returns JSON
    For now, this creates a single test tag programmatically to demonstrate
    the Ignition integration. File parsing will be implemented in Phase 2.
    """
    try:
        # Validate file type
        if file.filename:
            file_ext = Path(file.filename).suffix.lower()
            if file_ext not in settings.allowed_file_extensions:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type. Allowed extensions: {', '.join(settings.allowed_file_extensions)}"
                )
        
        # Read the uploaded file (for validation)
        content = await file.read()
        file_size = len(content)
        
        logger.info(f"Received file: {file.filename} ({file_size} bytes)")
        
        # Validate file size
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size is {settings.max_file_size} bytes"
            )
        
        # Phase 1 POC: Instead of parsing the file, create a hardcoded test tag
        logger.info("Phase 1 POC: Creating a single test tag programmatically...")
        
        # Create a minimal tag via Ignition Gateway REST API
        client = get_ignition_client()
        quality_codes = await client.create_minimal_tag(
            tag_name="POC_Test_Tag",
            tag_path="POC_Phase1"
        )
        
        # Interpret the result
        success = len(quality_codes) == 0
        
        if success:
            message = "Tag created successfully"
            result = TagImportResult(
                success=True,
                tag_path="POC_Phase1/POC_Test_Tag",
                message=message,
                quality_codes=[]
            )
        else:
            # Use model_dump() instead of manual dict conversion
            qc_list = [qc.model_dump() for qc in quality_codes]
            message = f"Tag import returned {len(quality_codes)} quality code(s)"
            result = TagImportResult(
                success=False,
                tag_path="POC_Phase1/POC_Test_Tag",
                message=message,
                quality_codes=qc_list
            )
        
        return UploadResponse(
            status="success" if success else "failed",
            message=message,
            tags_processed=1,
            results=[result]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        # Log the full error server-side, but don't expose details to the client
        logger.error(f"Error during upload: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error. Please check server logs for details."
        )


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "Ignition SCADA Tag Bulk Uploader",
        "version": __version__,
        "phase": "Phase 1 - POC",
        "endpoints": {
            "health": "/api/health",
            "upload": "/api/upload (POST)",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
