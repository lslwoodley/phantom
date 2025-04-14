# 📄 msgraph_client.py
# 📍 Location: backend/app/core/msgraph_client.py
# 🧠 Purpose: Handles MS Graph API token auth and snapshot ingestion (14-day scoped user context)

import requests
from app.config import get_settings
from typing import Dict, Optional
from datetime import datetime, timedelta

# Load shared environment settings
settings = get_settings()

class MSGraphClient:
    def __init__(self, access_token: str):
        # Initialize with the provided Microsoft Graph API token
        self.token = access_token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def get_recent_emails(self) -> Optional[Dict]:
        # Retrieve user's emails received in the last 14 days
        since = (datetime.utcnow() - timedelta(days=14)).isoformat() + 'Z'
        url = f"{self.base_url}/me/messages?$filter=receivedDateTime ge {since}&$top=10"
        response = requests.get(url, headers=self.headers)
        # Return parsed JSON if successful, otherwise None
        return response.json() if response.ok else None

    def get_recent_chats(self) -> Optional[Dict]:
        # Retrieve the 10 most recent chat sessions for the user
        url = f"{self.base_url}/me/chats?$top=10"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.ok else None

    def get_recent_drive_items(self) -> Optional[Dict]:
        # Retrieve user's most recently accessed OneDrive files
        url = f"{self.base_url}/me/drive/recent"
        response = requests.get(url, headers=self.headers)
        return response.json() if response.ok else None

    def snapshot_user_context(self) -> Dict:
        # Aggregate a snapshot of the user's recent context
        return {
            "emails": self.get_recent_emails(),
            "chats": self.get_recent_chats(),
            "files": self.get_recent_drive_items(),
            "timestamp": datetime.utcnow().isoformat()  # Include snapshot timestamp
        }

# ➕ Integration: Use MSGraphClient within PlannerAgent to enrich task planning with user context.
# Example usage (in planner.py):
# graph_client = MSGraphClient(user_token)
# context_snapshot = graph_client.snapshot_user_context()
