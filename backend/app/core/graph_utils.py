
from msal import ConfidentialClientApplication
import requests
import os

class GraphHelper:
    def __init__(self, tenant_id: str, client_id: str, client_secret: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_endpoint = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        self.scope = ["https://graph.microsoft.com/.default"]

        self.client = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}"
        )

    def acquire_token(self):
        result = self.client.acquire_token_for_client(scopes=self.scope)
        if "access_token" in result:
            return result["access_token"]
        raise Exception("Failed to acquire Graph API token.")

    def expand_groups(self, oid: str) -> list:
        token = self.acquire_token()
        headers = {"Authorization": f"Bearer {token}"}
        url = f"https://graph.microsoft.com/v1.0/users/{oid}/transitiveMemberOf/microsoft.graph.group?$select=id"
        groups = []

        while url:
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()
            groups.extend([g["id"] for g in data.get("value", [])])
            url = data.get("@odata.nextLink")

        return groups
