# 📄 blob_logger.py
# 📍 Location: backend/app/utils/blob_logger.py
# 🧠 Purpose: Save JSON telemetry logs to Azure Blob Storage

import json
from azure.storage.blob import BlobServiceClient
from app.config import get_settings
from datetime import datetime

settings = get_settings()

def upload_telemetry_to_blob(data: dict, user_id: str):
    # Prepare blob client and path
    blob_service = BlobServiceClient.from_connection_string(settings.azure_blob_conn_str)
    container_client = blob_service.get_container_client(settings.blob_container)

    # Use timestamped blob name
    timestamp = datetime.utcnow().isoformat().replace(':', '-')
    blob_name = f"telemetry/{user_id}/{timestamp}.json"

    # Convert to bytes and upload
    json_data = json.dumps(data, indent=2)
    container_client.upload_blob(name=blob_name, data=json_data, overwrite=True)

    return blob_name

def list_telemetry_logs(user_id: str = None) -> list:
    blob_service = BlobServiceClient.from_connection_string(settings.azure_blob_conn_str)
    container_client = blob_service.get_container_client(settings.blob_container)

    prefix = f"telemetry/{user_id}/" if user_id else "telemetry/"
    blob_list = container_client.list_blobs(name_starts_with=prefix)

    return [{"name": b.name, "last_modified": b.last_modified.isoformat()} for b in blob_list]

def get_telemetry_log(blob_name: str) -> dict:
    blob_service = BlobServiceClient.from_connection_string(settings.azure_blob_conn_str)
    container_client = blob_service.get_container_client(settings.blob_container)
    
    blob_client = container_client.get_blob_client(blob_name)
    download = blob_client.download_blob()
    content = download.readall()
    
    return json.loads(content)
