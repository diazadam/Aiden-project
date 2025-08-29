"""
🔌 AIDEN UNIFIED CONNECTOR LAYER V1
Bulletproof async API wrappers for all external services.
"""

import asyncio
import httpx
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field
from datetime import datetime
import json
import base64
from pathlib import Path

from .secrets import secrets_manager


@dataclass
class ConnectorResponse:
    """Standardized response format for all connectors"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    connector: str = ""
    execution_time_ms: float = 0.0


class BaseConnector:
    """Base class for all API connectors"""
    
    def __init__(self, name: str):
        self.name = name
        self.secrets = secrets_manager.secrets
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if not self._client:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client
    
    async def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict] = None,
        data: Optional[Any] = None,
        json_data: Optional[Dict] = None
    ) -> ConnectorResponse:
        """Make HTTP request with standardized response"""
        start_time = asyncio.get_event_loop().time()
        
        try:
            client = await self._get_client()
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data
            )
            
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            
            if response.status_code >= 400:
                return ConnectorResponse(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text}",
                    connector=self.name,
                    execution_time_ms=execution_time
                )
            
            try:
                response_data = response.json()
            except:
                response_data = response.text
            
            return ConnectorResponse(
                success=True,
                data=response_data,
                connector=self.name,
                execution_time_ms=execution_time,
                metadata={"status_code": response.status_code}
            )
            
        except Exception as e:
            execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
            return ConnectorResponse(
                success=False,
                error=str(e),
                connector=self.name,
                execution_time_ms=execution_time
            )
    
    async def health_check(self) -> ConnectorResponse:
        """Check connector health - override in subclasses"""
        return ConnectorResponse(
            success=True,
            data={"status": "healthy"},
            connector=self.name
        )
    
    async def close(self):
        """Close HTTP client"""
        if self._client:
            await self._client.aclose()


class OpenAIConnector(BaseConnector):
    """OpenAI API connector with full chat completions support"""
    
    def __init__(self):
        super().__init__("openai")
        self.base_url = "https://api.openai.com/v1"
    
    async def health_check(self) -> ConnectorResponse:
        """Check OpenAI API health"""
        if not self.secrets.openai_api_key:
            return ConnectorResponse(
                success=False,
                error="OpenAI API key not configured",
                connector=self.name
            )
        
        try:
            response = await self._make_request(
                "GET",
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.secrets.openai_api_key}"}
            )
            
            if response.success:
                models_count = len(response.data.get("data", []))
                response.data = {"status": "healthy", "models_available": models_count}
            
            return response
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e),
                connector=self.name
            )
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4-turbo-preview",
        max_tokens: int = 2000,
        temperature: float = 0.7,
        **kwargs
    ) -> ConnectorResponse:
        """Create chat completion"""
        if not self.secrets.openai_api_key:
            return ConnectorResponse(
                success=False,
                error="OpenAI API key not configured",
                connector=self.name
            )
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            **kwargs
        }
        
        return await self._make_request(
            "POST",
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.secrets.openai_api_key}",
                "Content-Type": "application/json"
            },
            json_data=payload
        )


class AnthropicConnector(BaseConnector):
    """Anthropic Claude API connector"""
    
    def __init__(self):
        super().__init__("anthropic")
        self.base_url = "https://api.anthropic.com/v1"
    
    async def health_check(self) -> ConnectorResponse:
        """Check Anthropic API health"""
        if not self.secrets.anthropic_api_key:
            return ConnectorResponse(
                success=False,
                error="Anthropic API key not configured",
                connector=self.name
            )
        
        # Anthropic doesn't have a models endpoint, so we'll do a minimal message
        return await self.create_message(
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=5
        )
    
    async def create_message(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 1000,
        **kwargs
    ) -> ConnectorResponse:
        """Create Claude message"""
        if not self.secrets.anthropic_api_key:
            return ConnectorResponse(
                success=False,
                error="Anthropic API key not configured",
                connector=self.name
            )
        
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        return await self._make_request(
            "POST",
            f"{self.base_url}/messages",
            headers={
                "x-api-key": self.secrets.anthropic_api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            },
            json_data=payload
        )


class ElevenLabsConnector(BaseConnector):
    """ElevenLabs TTS API connector"""
    
    def __init__(self):
        super().__init__("elevenlabs")
        self.base_url = "https://api.elevenlabs.io/v1"
    
    async def health_check(self) -> ConnectorResponse:
        """Check ElevenLabs API health"""
        if not self.secrets.elevenlabs_api_key:
            return ConnectorResponse(
                success=False,
                error="ElevenLabs API key not configured",
                connector=self.name
            )
        
        response = await self._make_request(
            "GET",
            f"{self.base_url}/voices",
            headers={"xi-api-key": self.secrets.elevenlabs_api_key}
        )
        
        if response.success:
            voices_count = len(response.data.get("voices", []))
            response.data = {"status": "healthy", "voices_available": voices_count}
        
        return response
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        **kwargs
    ) -> ConnectorResponse:
        """Convert text to speech"""
        if not self.secrets.elevenlabs_api_key:
            return ConnectorResponse(
                success=False,
                error="ElevenLabs API key not configured",
                connector=self.name
            )
        
        voice_id = voice_id or self.secrets.elevenlabs_voice_id
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            },
            **kwargs
        }
        
        return await self._make_request(
            "POST",
            f"{self.base_url}/text-to-speech/{voice_id}",
            headers={
                "xi-api-key": self.secrets.elevenlabs_api_key,
                "Content-Type": "application/json"
            },
            json_data=payload
        )


class SupabaseConnector(BaseConnector):
    """Supabase API connector"""
    
    def __init__(self):
        super().__init__("supabase")
    
    async def health_check(self) -> ConnectorResponse:
        """Check Supabase connection"""
        if not (self.secrets.supabase_url and self.secrets.supabase_service_role_key):
            return ConnectorResponse(
                success=False,
                error="Supabase credentials not configured",
                connector=self.name
            )
        
        response = await self._make_request(
            "GET",
            f"{self.secrets.supabase_url}/rest/v1/",
            headers={
                "apikey": self.secrets.supabase_service_role_key,
                "Authorization": f"Bearer {self.secrets.supabase_service_role_key}"
            }
        )
        
        if response.success or response.metadata.get("status_code") == 404:
            response.success = True
            response.data = {"status": "healthy", "connection": "established"}
            response.error = None
        
        return response
    
    async def query(
        self,
        table: str,
        select: str = "*",
        filters: Optional[Dict] = None,
        **kwargs
    ) -> ConnectorResponse:
        """Query Supabase table"""
        if not (self.secrets.supabase_url and self.secrets.supabase_service_role_key):
            return ConnectorResponse(
                success=False,
                error="Supabase credentials not configured",
                connector=self.name
            )
        
        url = f"{self.secrets.supabase_url}/rest/v1/{table}?select={select}"
        
        if filters:
            for key, value in filters.items():
                url += f"&{key}={value}"
        
        return await self._make_request(
            "GET",
            url,
            headers={
                "apikey": self.secrets.supabase_service_role_key,
                "Authorization": f"Bearer {self.secrets.supabase_service_role_key}"
            }
        )
    
    async def insert(self, table: str, data: Dict) -> ConnectorResponse:
        """Insert data into Supabase table"""
        if not (self.secrets.supabase_url and self.secrets.supabase_service_role_key):
            return ConnectorResponse(
                success=False,
                error="Supabase credentials not configured",
                connector=self.name
            )
        
        return await self._make_request(
            "POST",
            f"{self.secrets.supabase_url}/rest/v1/{table}",
            headers={
                "apikey": self.secrets.supabase_service_role_key,
                "Authorization": f"Bearer {self.secrets.supabase_service_role_key}",
                "Content-Type": "application/json"
            },
            json_data=data
        )


class GoogleCloudConnector(BaseConnector):
    """Google Cloud Storage connector"""
    
    def __init__(self):
        super().__init__("google_cloud")
        self.project_id = self.secrets.gcp_project_id or "gen-lang-client-0093497568"
    
    async def health_check(self) -> ConnectorResponse:
        """Check Google Cloud connectivity"""
        try:
            from google.cloud import storage
            client = storage.Client(project=self.project_id)
            
            # Test with list buckets
            buckets = list(client.list_buckets(max_results=1))
            
            return ConnectorResponse(
                success=True,
                data={"status": "healthy", "project": self.project_id},
                connector=self.name
            )
            
        except ImportError:
            return ConnectorResponse(
                success=False,
                error="google-cloud-storage package not installed",
                connector=self.name
            )
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e),
                connector=self.name
            )
    
    async def create_bucket(self, bucket_name: str, location: str = "US") -> ConnectorResponse:
        """Create Google Cloud Storage bucket"""
        try:
            from google.cloud import storage
            client = storage.Client(project=self.project_id)
            
            bucket = client.create_bucket(bucket_name, location=location)
            
            return ConnectorResponse(
                success=True,
                data={"bucket_name": bucket_name, "location": location},
                connector=self.name
            )
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e),
                connector=self.name
            )
    
    async def upload_file(
        self,
        bucket_name: str,
        file_path: str,
        blob_name: str,
        content_type: str = "text/html",
        make_public: bool = True
    ) -> ConnectorResponse:
        """Upload file to Google Cloud Storage"""
        try:
            from google.cloud import storage
            client = storage.Client(project=self.project_id)
            
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(blob_name)
            
            with open(file_path, 'rb') as f:
                blob.upload_from_file(f, content_type=content_type)
            
            if make_public:
                blob.make_public()
            
            public_url = f"https://storage.googleapis.com/{bucket_name}/{blob_name}"
            
            return ConnectorResponse(
                success=True,
                data={
                    "bucket": bucket_name,
                    "blob": blob_name,
                    "url": public_url,
                    "public": make_public
                },
                connector=self.name
            )
            
        except Exception as e:
            return ConnectorResponse(
                success=False,
                error=str(e),
                connector=self.name
            )


class UnifiedConnectorManager:
    """Unified manager for all API connectors"""
    
    def __init__(self):
        self.connectors = {
            "openai": OpenAIConnector(),
            "anthropic": AnthropicConnector(),
            "elevenlabs": ElevenLabsConnector(),
            "supabase": SupabaseConnector(),
            "google_cloud": GoogleCloudConnector()
        }
    
    async def health_check_all(self) -> Dict[str, ConnectorResponse]:
        """Run health checks on all connectors"""
        results = {}
        
        tasks = [
            (name, connector.health_check())
            for name, connector in self.connectors.items()
        ]
        
        for name, task in tasks:
            try:
                result = await task
                results[name] = result
            except Exception as e:
                results[name] = ConnectorResponse(
                    success=False,
                    error=str(e),
                    connector=name
                )
        
        return results
    
    def get_connector(self, name: str) -> Optional[BaseConnector]:
        """Get specific connector"""
        return self.connectors.get(name)
    
    async def close_all(self):
        """Close all connector connections"""
        for connector in self.connectors.values():
            await connector.close()
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_all()


# Global connector manager instance
connector_manager = UnifiedConnectorManager()


async def get_connector(name: str) -> Optional[BaseConnector]:
    """Get connector by name"""
    return connector_manager.get_connector(name)


async def health_check_all_connectors() -> Dict[str, ConnectorResponse]:
    """Run health checks on all connectors"""
    return await connector_manager.health_check_all()


# Export key classes and functions
__all__ = [
    "ConnectorResponse",
    "BaseConnector", 
    "OpenAIConnector",
    "AnthropicConnector", 
    "ElevenLabsConnector",
    "SupabaseConnector",
    "GoogleCloudConnector",
    "UnifiedConnectorManager",
    "connector_manager",
    "get_connector",
    "health_check_all_connectors"
]