"""Unit tests for Pydantic models"""

import pytest
from app.models import (
    HealthResponse,
    TagImportResult,
    UploadResponse,
    ApiTokenResponse,
    QualityCode
)


class TestHealthResponse:
    """Tests for HealthResponse model"""
    
    def test_create_valid_health_response(self):
        """Test creating a valid health response"""
        response = HealthResponse(
            status="healthy",
            version="1.0.0",
            ignition_connected=True,
            ignition_gateway="http://localhost:8088"
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"
        assert response.ignition_connected is True
        assert response.ignition_gateway == "http://localhost:8088"
    
    def test_health_response_json_serialization(self):
        """Test JSON serialization"""
        response = HealthResponse(
            status="degraded",
            version="1.0.0",
            ignition_connected=False,
            ignition_gateway="http://localhost:8088"
        )
        
        json_data = response.model_dump()
        assert json_data["status"] == "degraded"
        assert json_data["ignition_connected"] is False


class TestTagImportResult:
    """Tests for TagImportResult model"""
    
    def test_create_successful_result(self):
        """Test creating a successful tag import result"""
        result = TagImportResult(
            success=True,
            tag_path="Folder/Tag1",
            message="Tag created successfully",
            quality_codes=[]
        )
        
        assert result.success is True
        assert result.tag_path == "Folder/Tag1"
        assert result.message == "Tag created successfully"
        assert result.quality_codes == []
    
    def test_create_failed_result_with_quality_codes(self):
        """Test creating a failed result with quality codes"""
        qc = {"level": "ERROR", "userCode": 100, "diagnosticMessage": "Test error"}
        result = TagImportResult(
            success=False,
            tag_path="Folder/BadTag",
            message="Tag import failed",
            quality_codes=[qc]
        )
        
        assert result.success is False
        assert len(result.quality_codes) == 1
        assert result.quality_codes[0]["diagnosticMessage"] == "Test error"


class TestUploadResponse:
    """Tests for UploadResponse model"""
    
    def test_create_upload_response(self):
        """Test creating an upload response"""
        result = TagImportResult(
            success=True,
            tag_path="Test/Tag",
            message="Created",
            quality_codes=[]
        )
        
        response = UploadResponse(
            status="success",
            message="Upload completed",
            tags_processed=1,
            results=[result]
        )
        
        assert response.status == "success"
        assert response.message == "Upload completed"
        assert response.tags_processed == 1
        assert len(response.results) == 1
    
    def test_upload_response_defaults(self):
        """Test default values"""
        response = UploadResponse(
            status="success",
            message="Test"
        )
        
        assert response.tags_processed == 0
        assert response.results == []


class TestApiTokenResponse:
    """Tests for ApiTokenResponse model"""
    
    def test_create_api_token_response(self):
        """Test creating an API token response"""
        response = ApiTokenResponse(
            key="test-api-key-12345",
            hash="test-hash-67890"
        )
        
        assert response.key == "test-api-key-12345"
        assert response.hash == "test-hash-67890"


class TestQualityCode:
    """Tests for QualityCode model"""
    
    def test_create_quality_code_full(self):
        """Test creating a quality code with all fields"""
        qc = QualityCode(
            level="ERROR",
            userCode=500,
            diagnosticMessage="Internal error occurred"
        )
        
        assert qc.level == "ERROR"
        assert qc.userCode == 500
        assert qc.diagnosticMessage == "Internal error occurred"
    
    def test_create_quality_code_partial(self):
        """Test creating a quality code with optional fields None"""
        qc = QualityCode(
            level="WARNING",
            userCode=None,
            diagnosticMessage=None
        )
        
        assert qc.level == "WARNING"
        assert qc.userCode is None
        assert qc.diagnosticMessage is None
    
    def test_quality_code_model_dump(self):
        """Test model_dump() method"""
        qc = QualityCode(
            level="INFO",
            userCode=200,
            diagnosticMessage="Success"
        )
        
        data = qc.model_dump()
        assert data["level"] == "INFO"
        assert data["userCode"] == 200
        assert data["diagnosticMessage"] == "Success"
