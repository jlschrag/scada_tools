"""Pydantic models for API requests and responses"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# === API Response Models ===

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status: healthy or unhealthy")
    version: str = Field(..., description="Application version")
    ignition_connected: bool = Field(..., description="Whether Ignition Gateway is reachable")
    ignition_gateway: str = Field(..., description="Ignition Gateway URL")


class TagImportResult(BaseModel):
    """Result of tag import operation"""
    success: bool = Field(..., description="Whether the tag was created successfully")
    tag_path: str = Field(..., description="Path of the tag that was imported")
    message: str = Field(..., description="Success or error message")
    quality_codes: List[Dict[str, Any]] = Field(default_factory=list, description="Quality codes from Ignition response")


class UploadResponse(BaseModel):
    """Response from file upload endpoint"""
    status: str = Field(..., description="Upload status: success, partial, or failed")
    message: str = Field(..., description="Summary message")
    tags_processed: int = Field(default=0, description="Number of tags processed")
    results: List[TagImportResult] = Field(default_factory=list, description="Detailed results per tag")


# === Ignition API Models ===

class ApiTokenGenerateRequest(BaseModel):
    """Request body for API token generation"""
    username: str = Field(..., description="Gateway username")
    password: str = Field(..., description="Gateway password")


class ApiTokenResponse(BaseModel):
    """Response from API token generation"""
    key: str = Field(..., description="API key to use in Authorization header")
    hash: str = Field(..., description="API key hash (stored on server)")


class QualityCode(BaseModel):
    """Quality code from Ignition tag import response"""
    level: Optional[str] = None
    userCode: Optional[int] = None
    diagnosticMessage: Optional[str] = None
