#!/bin/bash

# 📄 Location: scripts/create_phantom_env.sh
# 🧠 Purpose: Generate Phantom MVP .env file with MSGraph and Azure OpenAI configuration

ENV_FILE=".env"

echo "⚙️ Generating Phantom MVP .env configuration..."

cat > $ENV_FILE <<EOF
# =========================
# 🚀 Phantom MVP Environment
# =========================

# ✅ General
APP_NAME="Phantom AI Backend"
ENVIRONMENT="development"

# ✅ LightRAG
LIGHTRAG_URL="https://your-lightrag-endpoint"
LIGHTRAG_API_KEY="your-lightrag-api-key"

# ✅ Microsoft Graph Configuration
MSGRAPH_CLIENT_ID="your-msgraph-client-id"
MSGRAPH_CLIENT_SECRET="your-msgraph-client-secret"
MSGRAPH_TENANT_ID="your-tenant-id"
MSGRAPH_SCOPE="https://graph.microsoft.com/.default"

# ✅ Azure OpenAI Configuration
OPENAI_API_KEY="your-azure-openai-api-key"
OPENAI_API_VERSION="2024-12-01-preview"
OPENAI_ENDPOINT="https://your-openai-endpoint.openai.azure.com/"
OPENAI_DEPLOYMENT="gpt-4"
OPENAI_EMBEDDING_DEPLOYMENT="text-embedding-3-small"
OPENAI_EMBEDDING_DIM=1536

# ✅ Entra ID / Phantom RBAC
TENANT_ID="your-tenant-id"
CLIENT_ID="your-phantom-client-id"

# ✅ Phantom RBAC App
PHANTOM_TENANT_ID="ea3ec4a4-f2ae-4f29-95b7-c73bc669a504"
PHANTOM_APP_CLIENT_ID="36e4c9e4-aa15-4b6f-bd62-05ddec1be39c"
PHANTOM_APP_SECRET=""
EOF

echo "✅ .env file created successfully at project root."
