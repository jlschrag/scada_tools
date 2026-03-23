"""Ignition Gateway REST API client"""

import json
import logging
import httpx
from typing import List, Dict, Any, Optional
from app.config import settings
from app.models import ApiTokenResponse, QualityCode

logger = logging.getLogger(__name__)


class IgnitionClient:
    """Client for interacting with Ignition Gateway REST API"""
    
    def __init__(self):
        self.base_url = settings.ignition_gateway_url
        self.username = settings.ignition_username
        self.password = settings.ignition_password
        self.verify_ssl = settings.ignition_verify_ssl
        self.api_token: Optional[str] = None
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create shared HTTP client for connection pooling"""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                verify=self.verify_ssl,
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
            )
        return self._http_client
    
    async def close(self):
        """Close the HTTP client"""
        if self._http_client is not None and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None
    
    async def check_connectivity(self) -> bool:
        """Check if the Ignition Gateway is reachable"""
        try:
            client = await self._get_client()
            # Try to access the API documentation endpoint
            response = await client.get(f"{self.base_url}/system/gwinfo", timeout=5.0)
            logger.info("Connectivity check successful")
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Connectivity check failed: {type(e).__name__}")
            logger.debug(f"Connectivity error details: {e}", exc_info=True)
            return False
    
    async def generate_api_token(self) -> ApiTokenResponse:
        """
        Generate an API token for authenticating with Ignition Gateway.
        
        Endpoint: POST /data/api/v1/api-token/generate
        
        Returns:
            ApiTokenResponse with key and hash
        """
        url = f"{self.base_url}/data/api/v1/api-token/generate"
        payload = {
            "username": self.username,
            "password": self.password
        }
        
        client = await self._get_client()
        response = await client.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        
        data = response.json()
        token_response = ApiTokenResponse(key=data["key"], hash=data["hash"])
        
        # Store the API key for subsequent requests
        self.api_token = token_response.key
        
        logger.info("API token generated successfully")
        logger.debug("API token obtained (not logging token value for security)")
        
        return token_response
    
    async def export_tag(self, tag_path: str, provider: str = "default") -> Dict[str, Any]:
        """
        Export an existing tag to understand the JSON format.
        
        Endpoint: GET /data/api/v1/tags/export
        
        Args:
            tag_path: Path to the tag (e.g., "Folder/TagName")
            provider: Tag provider name (default: "default")
        
        Returns:
            Tag export JSON
            
        Note: This method is currently unused but kept for debugging/exploration.
        """
        if not self.api_token:
            await self.generate_api_token()
        
        url = f"{self.base_url}/data/api/v1/tags/export"
        params = {
            "provider": provider,
            "type": "json",
            "path": tag_path
        }
        
        try:
            client = await self._get_client()
            response = await client.get(
                url,
                params=params,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Accept": "application/json"
                }
            )
            response.raise_for_status()
            
            # The response is JSON text, parse it
            export_data = response.json()
            logger.info(f"Exported tag '{tag_path}' successfully")
            logger.debug(f"Tag export format: {json.dumps(export_data, indent=2)[:500]}...")
            
            return export_data
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                logger.warning("API token expired or invalid, regenerating...")
                await self.generate_api_token()
                # Retry once with new token
                return await self.export_tag(tag_path, provider)
            raise
    
    async def import_tag(
        self,
        tag_json: Dict[str, Any],
        provider: str = "default",
        collision_policy: str = "Overwrite",
        _retry: bool = True
    ) -> List[QualityCode]:
        """
        Import a tag into Ignition.
        
        Endpoint: POST /data/api/v1/tags/import
        
        Args:
            tag_json: Tag definition in Ignition JSON export format
            provider: Tag provider name (default: "default")
            collision_policy: How to handle existing tags (Abort, Overwrite, Rename, Ignore, MergeOverwrite)
            _retry: Internal flag to prevent infinite retry loop
        
        Returns:
            List of QualityCode objects (empty list = success)
        """
        if not self.api_token:
            await self.generate_api_token()
        
        url = f"{self.base_url}/data/api/v1/tags/import"
        params = {
            "provider": provider,
            "type": "json",
            "collisionPolicy": collision_policy
        }
        
        # Convert tag JSON to bytes (application/octet-stream)
        tag_json_bytes = json.dumps(tag_json).encode("utf-8")
        
        try:
            client = await self._get_client()
            response = await client.post(
                url,
                params=params,
                content=tag_json_bytes,
                headers={
                    "Authorization": f"Bearer {self.api_token}",
                    "Content-Type": "application/octet-stream"
                }
            )
            response.raise_for_status()
            
            # Parse quality codes from response
            quality_codes_data = response.json()
            quality_codes = [QualityCode(**qc) for qc in quality_codes_data]
            
            if not quality_codes:
                logger.info("Tag imported successfully (empty quality codes)")
            else:
                logger.warning(f"Tag import returned {len(quality_codes)} quality code(s)")
                for qc in quality_codes:
                    logger.warning(f"  Quality code - Level: {qc.level}, Code: {qc.userCode}, Message: {qc.diagnosticMessage}")
            
            return quality_codes
            
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401 and _retry:
                logger.warning("API token expired or invalid, regenerating...")
                self.api_token = None
                await self.generate_api_token()
                # Retry once with new token
                return await self.import_tag(tag_json, provider, collision_policy, _retry=False)
            raise
    
    async def create_minimal_tag(self, tag_name: str, tag_path: str = "") -> List[QualityCode]:
        """
        Create a minimal OPC tag for Phase 1 POC.
        
        This constructs a simple tag JSON matching the Ignition export format.
        
        Args:
            tag_name: Name of the tag
            tag_path: Folder path (e.g., "TestFolder")
        
        Returns:
            List of QualityCode objects (empty = success)
        """
        # Construct minimal tag JSON based on typical Ignition export format
        # This is a starting point - may need adjustment based on actual export format
        full_path = f"{tag_path}/{tag_name}" if tag_path else tag_name
        
        tag_json = {
            "tags": [
                {
                    "name": tag_name,
                    "path": tag_path,
                    "tagType": "AtomicTag",
                    "dataType": "Int4",
                    "valueSource": "opc",
                    "enabled": True,
                    "opcServer": settings.opc_server_name,  # Use configurable OPC server name
                    "opcItemPath": f"[device]path/to/{tag_name}",
                    "documentation": "Phase 1 POC test tag created programmatically"
                }
            ]
        }
        
        logger.info(f"Creating minimal tag: {full_path}")
        logger.debug(f"Tag JSON: {json.dumps(tag_json, indent=2)}")
        
        return await self.import_tag(tag_json)


# Singleton instance - initialized lazily to avoid loading settings at import time
_ignition_client: Optional[IgnitionClient] = None


def get_ignition_client() -> IgnitionClient:
    """Get or create the singleton IgnitionClient instance"""
    global _ignition_client
    if _ignition_client is None:
        _ignition_client = IgnitionClient()
    return _ignition_client


# For backward compatibility, but prefer using get_ignition_client()
ignition_client = get_ignition_client()
