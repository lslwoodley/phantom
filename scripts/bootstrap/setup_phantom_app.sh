#!/bin/bash
set -e

echo "🔐 Logging into Azure CLI..."
az login

# === CONFIG ===================================================================
BASE_NAME="PhantomApp"
REDIRECT_URI="http://localhost"
GRAPH_API_ID="00000003-0000-0000-c000-000000000000"

declare -a PERMISSIONS=(
  "e383f46e-2787-4529-855e-0e479a3ffac0"   # Mail.Read
  "465a38f9-76ea-45b9-9f34-9e8b0d4c0f3e"   # Calendars.Read
  "b340eb25-3456-403f-be2f-af7a0d370277"   # Chat.Read
  "10465720-29dd-4523-a11a-6a75c743c9d9"   # Files.Read.All
)
# ==============================================================================

TIMESTAMP=$(date +%s)
APP_NAME="$BASE_NAME"

echo "🔍 Checking for existing app '$APP_NAME'..."
existing_id=$(az ad app list --display-name "$APP_NAME" --query "[0].appId" -o tsv)

if [[ -n "$existing_id" ]]; then
  echo "⚠️  Name conflict detected (appId=$existing_id)."
  APP_NAME="${BASE_NAME}-${TIMESTAMP}"
  echo "🔄  Using unique name '$APP_NAME'."
fi

echo "🚀 Creating app registration..."
app_id=$(az ad app create \
  --display-name "$APP_NAME" \
  --sign-in-audience AzureADMyOrg \
  --web-redirect-uris "$REDIRECT_URI" \
  --query "appId" -o tsv)

echo "🔐 Creating service principal..."
az ad sp create --id "$app_id"

echo "🔑 Generating client secret..."
client_secret=$(az ad app credential reset --id "$app_id" --append \
  --display-name "PhantomSecret" \
  --years 1 --query "password" -o tsv)

echo "🔗 Assigning Microsoft Graph API permissions..."
for perm in "${PERMISSIONS[@]}"; do
  az ad app permission add \
    --id "$app_id" \
    --api "$GRAPH_API_ID" \
    --api-permissions "${perm}=Scope"
done

echo "🧾 Granting admin consent..."
az ad app permission admin-consent --id "$app_id"

tenant_id=$(az account show --query tenantId -o tsv)

echo "📄 Writing .env ..."
cat > .env <<EOF
phantom_tenant_id=$tenant_id
phantom_app_client_id=$app_id
phantom_app_secret=$client_secret

msgraph_client_id=$app_id
msgraph_client_secret=$client_secret
msgraph_tenant_id=$tenant_id
msgraph_scope=https://graph.microsoft.com/.default

openai_api_key=
openai_api_version=2024-12-01-preview
openai_endpoint=https://aoai-e7gh5iceqsisa.openai.azure.com/
openai_deployment=gpt-4
openai_embedding_deployment=text-embedding-3-small
openai_embedding_dim=1536
EOF

echo "✅ Phantom App setup complete! (.env generated)"
