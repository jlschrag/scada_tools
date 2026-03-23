"""Configuration management for the FastAPI application"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Server settings
    api_host: str = "0.0.0.0"
    api_port: int = 8080
    api_reload: bool = False
    log_level: str = "INFO"  # Logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
    
    # Ignition Gateway settings
    ignition_gateway_url: str = "http://localhost:8088"
    ignition_username: str  # Required - no default for security
    ignition_password: str  # Required - no default for security
    ignition_verify_ssl: bool = False  # Disable SSL verification for self-signed certs
    
    # Tag provider settings
    tag_provider: str = "default"
    opc_server_name: str = "Ignition OPC UA Server"  # Configurable OPC server name
    
    # Upload settings
    max_file_size: int = 10485760  # 10MB in bytes
    allowed_file_extensions: list[str] = [".csv", ".xlsx", ".xls"]  # Allowed upload file types
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Singleton instance
# Note: Since credentials are required, ensure IGNITION_USERNAME and IGNITION_PASSWORD
# are set in environment variables or .env file before importing this module.
settings = Settings()
