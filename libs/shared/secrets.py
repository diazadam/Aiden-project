"""
🔐 AIDEN SECRETS MANAGEMENT
Bulletproof secrets validation and management system.
"""

import os
import base64
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

class SecretsSchema(BaseModel):
    """Comprehensive secrets validation schema"""
    
    # === LLM APIs ===
    openai_api_key: Optional[str] = Field(None, min_length=40, description="OpenAI API Key")
    anthropic_api_key: Optional[str] = Field(None, min_length=40, description="Anthropic API Key")
    
    # === Speech & Audio ===
    use_elevenlabs: bool = Field(False, description="Enable ElevenLabs TTS")
    elevenlabs_api_key: Optional[str] = Field(None, description="ElevenLabs API Key")
    elevenlabs_voice_id: str = Field("21m00Tcm4TlvDq8ikWAM", description="ElevenLabs Voice ID")
    
    # === Aiden Core ===
    aiden_pin: str = Field("4242", description="Aiden security PIN")
    speak_replies: bool = Field(True, description="Enable voice replies")
    
    # === Database & Storage ===
    supabase_url: Optional[str] = Field(None, description="Supabase project URL")
    supabase_anon_key: Optional[str] = Field(None, description="Supabase anon key")
    supabase_service_role_key: Optional[str] = Field(None, description="Supabase service role key")
    supabase_jwt: Optional[str] = Field(None, description="Supabase JWT token")
    supabase_db_password: Optional[str] = Field(None, description="Supabase database password")
    
    # === Google Cloud Platform ===
    gcp_project_id: Optional[str] = Field(None, description="Google Cloud Project ID")
    gcp_region: str = Field("us-central1", description="Google Cloud region")
    gcp_sa_json_base64: Optional[str] = Field(None, description="Base64 encoded service account JSON")
    gcp_sa_path: str = Field("./gcp_service_account.json", description="Service account JSON file path")
    google_cloud_project: Optional[str] = Field(None, description="Google Cloud project (legacy)")
    google_ai_api_key: Optional[str] = Field(None, description="Google AI API key")
    
    # === Vector & AI Services ===
    pinecone_api_key: Optional[str] = Field(None, description="Pinecone API key")
    langchain_api_key: Optional[str] = Field(None, description="LangChain API key")
    cohere_api_key: Optional[str] = Field(None, description="Cohere API key")
    weaviate_api_key: Optional[str] = Field(None, description="Weaviate API key")
    
    # === Development ===
    cursor_api_key: Optional[str] = Field(None, description="Cursor API key")
    
    # === Automation ===
    n8n_url: Optional[str] = Field(None, description="n8n automation URL")
    n8n_token: Optional[str] = Field(None, description="n8n API token")
    
    # === iOS Development (Future) ===
    apple_developer_team_id: Optional[str] = Field(None, description="Apple Developer Team ID")
    apple_key_id: Optional[str] = Field(None, description="Apple API Key ID")
    apple_private_key: Optional[str] = Field(None, description="Apple Private Key")
    fastlane_session: Optional[str] = Field(None, description="Fastlane session token")
    
    # === Billing & Revenue (Future) ===
    stripe_secret_key: Optional[str] = Field(None, description="Stripe secret key")
    stripe_webhook_secret: Optional[str] = Field(None, description="Stripe webhook secret")
    
    @validator('openai_api_key')
    def validate_openai_key(cls, v):
        if v and not v.startswith('sk-'):
            raise ValueError('OpenAI API key must start with sk-')
        return v
    
    @validator('anthropic_api_key')
    def validate_anthropic_key(cls, v):
        if v and not v.startswith('sk-ant-'):
            raise ValueError('Anthropic API key must start with sk-ant-')
        return v
    
    @validator('supabase_url')
    def validate_supabase_url(cls, v):
        if v and not v.startswith('https://'):
            raise ValueError('Supabase URL must start with https://')
        return v
    
    @validator('gcp_sa_json_base64')
    def validate_gcp_json(cls, v):
        if v:
            try:
                base64.b64decode(v)
            except Exception:
                raise ValueError('GCP service account JSON must be valid base64')
        return v

class SecretsManager:
    """Manage and validate all Aiden secrets"""
    
    def __init__(self, env_file: Optional[str] = None):
        self.env_file = env_file or ".env.local"
        self.secrets: Optional[SecretsSchema] = None
        self._load_secrets()
    
    def _load_secrets(self):
        """Load and validate secrets from environment"""
        # Load from .env.local file
        load_dotenv(self.env_file, override=True)
        
        # Create secrets dict from environment variables
        secrets_dict = {}
        
        # Map environment variables to schema fields
        env_mapping = {
            'OPENAI_API_KEY': 'openai_api_key',
            'ANTHROPIC_API_KEY': 'anthropic_api_key',
            'USE_ELEVENLABS': 'use_elevenlabs',
            'ELEVENLABS_API_KEY': 'elevenlabs_api_key',
            'ELEVENLABS_VOICE_ID': 'elevenlabs_voice_id',
            'AIDEN_PIN': 'aiden_pin',
            'SPEAK_REPLIES': 'speak_replies',
            'SUPABASE_URL': 'supabase_url',
            'SUPABASE_ANON_KEY': 'supabase_anon_key',
            'SUPABASE_SERVICE_ROLE_KEY': 'supabase_service_role_key',
            'SUPABASE_JWT': 'supabase_jwt',
            'SUPABASE_DB_PASSWORD': 'supabase_db_password',
            'GCP_PROJECT_ID': 'gcp_project_id',
            'GCP_REGION': 'gcp_region',
            'GCP_SA_JSON_BASE64': 'gcp_sa_json_base64',
            'GCP_SA_PATH': 'gcp_sa_path',
            'GOOGLE_CLOUD_PROJECT': 'google_cloud_project',
            'GOOGLE_AI_API_KEY': 'google_ai_api_key',
            'PINECONE_API_KEY': 'pinecone_api_key',
            'LANGCHAIN_API_KEY': 'langchain_api_key',
            'COHERE_API_KEY': 'cohere_api_key',
            'WEAVIATE_API_KEY': 'weaviate_api_key',
            'CURSOR_API_KEY': 'cursor_api_key',
            'N8N_URL': 'n8n_url',
            'N8N_TOKEN': 'n8n_token',
        }
        
        for env_var, field_name in env_mapping.items():
            value = os.getenv(env_var)
            if value:
                # Convert boolean strings
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                secrets_dict[field_name] = value
        
        try:
            self.secrets = SecretsSchema(**secrets_dict)
        except Exception as e:
            raise ValueError(f"Invalid secrets configuration: {e}")
    
    def get_secret(self, key: str) -> Any:
        """Get a specific secret value"""
        if not self.secrets:
            raise ValueError("Secrets not loaded")
        return getattr(self.secrets, key, None)
    
    def validate_required_for_service(self, service: str) -> Dict[str, bool]:
        """Validate secrets required for a specific service"""
        validations = {}
        
        if service == "openai":
            validations["openai_api_key"] = bool(self.secrets.openai_api_key)
        
        elif service == "anthropic":
            validations["anthropic_api_key"] = bool(self.secrets.anthropic_api_key)
        
        elif service == "elevenlabs":
            validations["elevenlabs_api_key"] = bool(self.secrets.elevenlabs_api_key)
        
        elif service == "supabase":
            validations["supabase_url"] = bool(self.secrets.supabase_url)
            validations["supabase_service_role_key"] = bool(self.secrets.supabase_service_role_key)
        
        elif service == "gcp":
            validations["gcp_project_id"] = bool(self.secrets.gcp_project_id)
            validations["gcp_credentials"] = bool(
                self.secrets.gcp_sa_json_base64 or 
                Path(self.secrets.gcp_sa_path).exists()
            )
        
        return validations
    
    def get_masked_summary(self) -> Dict[str, str]:
        """Get a summary of secrets with masked values for logging"""
        if not self.secrets:
            return {}
        
        summary = {}
        for field_name, field_value in self.secrets.dict().items():
            if field_value is None:
                summary[field_name] = "❌ Not set"
            elif isinstance(field_value, bool):
                summary[field_name] = "✅ Enabled" if field_value else "❌ Disabled"
            elif isinstance(field_value, str):
                if len(field_value) > 10:
                    summary[field_name] = f"✅ {field_value[:4]}...{field_value[-4:]}"
                else:
                    summary[field_name] = f"✅ {field_value[:2]}..."
            else:
                summary[field_name] = f"✅ Set ({type(field_value).__name__})"
        
        return summary

# Global secrets manager instance
secrets_manager = SecretsManager()

def get_secrets() -> SecretsSchema:
    """Get the global secrets instance"""
    return secrets_manager.secrets

def get_secret(key: str) -> Any:
    """Get a specific secret value"""
    return secrets_manager.get_secret(key)