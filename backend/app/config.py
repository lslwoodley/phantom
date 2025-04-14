# 📄 config.py
# 📍 Location: backend/app/config.py
# 🧠 Purpose: Central place to load and manage .env settings for the Phantom backend

from pydantic import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # General
    app_name: str = "Phantom AI Backend"
    environment: str = "development"

    # LightRAG
    lightrag_url: str
    lightrag_api_key: str

    # MSGraph
    msgraph_client_id: str
    msgraph_client_secret: str
    msgraph_tenant_id: str
    msgraph_scope: str

    # OpenAI
    openai_api_key: str
    openai_api_version: str
    openai_endpoint: str
    openai_deployment: str
    openai_embedding_deployment: str
    openai_embedding_dim: int = 1536

    # Entra ID
    tenant_id: str
    client_id: str

    class Config:
        env_file = ".env"

# Centralized RBAC role groups for Phantom
ROLE_GROUPS = {
    "phantom_admin": ["platform_admin", "data_engineer", "data_scientist"],
    "compliance_group": ["compliance_admin", "compliance_user"],
    "viewer_group": ["read_only"]
}

@lru_cache()
def get_settings():
    return Settings()
