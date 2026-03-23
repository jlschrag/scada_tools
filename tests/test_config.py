"""Unit tests for configuration module"""

import os
import pytest
from pydantic import ValidationError

# Ensure required env vars are set before importing Settings
os.environ.setdefault("IGNITION_USERNAME", "test_user")
os.environ.setdefault("IGNITION_PASSWORD", "test_password")

from app.config import Settings


def test_settings_with_required_fields():
    """Test that settings can be created with required fields"""
    settings = Settings(
        ignition_username="test_user",
        ignition_password="test_pass"
    )
    assert settings.ignition_username == "test_user"
    assert settings.ignition_password == "test_pass"
    assert settings.api_port == 8080  # Default value


def test_settings_missing_username(monkeypatch):
    """Test that settings fails without username"""
    # Clear any environment variables that might provide defaults
    monkeypatch.delenv("IGNITION_USERNAME", raising=False)
    monkeypatch.delenv("IGNITION_PASSWORD", raising=False)
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(ignition_password="test_pass", _env_file=None)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("ignition_username",) for e in errors)


def test_settings_missing_password(monkeypatch):
    """Test that settings fails without password"""
    # Clear any environment variables that might provide defaults
    monkeypatch.delenv("IGNITION_USERNAME", raising=False)
    monkeypatch.delenv("IGNITION_PASSWORD", raising=False)
    
    with pytest.raises(ValidationError) as exc_info:
        Settings(ignition_username="test_user", _env_file=None)
    
    errors = exc_info.value.errors()
    assert any(e["loc"] == ("ignition_password",) for e in errors)


def test_settings_defaults():
    """Test default values are applied correctly"""
    settings = Settings(
        ignition_username="test_user",
        ignition_password="test_pass"
    )
    
    assert settings.api_host == "0.0.0.0"
    assert settings.api_port == 8080
    assert settings.api_reload is False
    assert settings.log_level == "INFO"
    assert settings.ignition_gateway_url == "http://localhost:8088"
    assert settings.ignition_verify_ssl is False
    assert settings.tag_provider == "default"
    assert settings.opc_server_name == "Ignition OPC UA Server"
    assert settings.max_file_size == 10485760
    assert settings.allowed_file_extensions == [".csv", ".xlsx", ".xls"]


def test_settings_custom_values():
    """Test that custom values override defaults"""
    settings = Settings(
        ignition_username="custom_user",
        ignition_password="custom_pass",
        api_port=9000,
        log_level="DEBUG",
        ignition_gateway_url="https://prod.example.com:8043",
        tag_provider="production",
        opc_server_name="Custom OPC Server"
    )
    
    assert settings.api_port == 9000
    assert settings.log_level == "DEBUG"
    assert settings.ignition_gateway_url == "https://prod.example.com:8043"
    assert settings.tag_provider == "production"
    assert settings.opc_server_name == "Custom OPC Server"
