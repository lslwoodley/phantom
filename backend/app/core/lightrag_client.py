# 📄 lightrag_client.py
# 📍 Location: backend/app/core/lightrag_client.py
# 🧠 Purpose: Encapsulates interaction with the LightRAG server API for indexing documents and querying with dual-level retrieval modes

# 📄 lightrag_client.py
# 📍 Location: backend/app/core/lightrag_client.py
# 🧠 Purpose: Async interaction with the LightRAG server API for indexing and querying documents

import aiohttp
from typing import List, Dict
from app.config import get_settings

settings = get_settings()

class LightRAGClient:
    def __init__(self):
        self.base_url = settings.lightrag_url
        self.headers = {
            "X-API-Key": settings.lightrag_api_key,
            "Content-Type": "application/json"
        }

    async def index_documents(self, user_id: str, documents: List[str]) -> Dict:
        """
        Index a list of documents into LightRAG for a specific user.
        """
        url = f"{self.base_url}/index"
        payload = {
            "documents": documents,
            "metadata": {"user_id": user_id}
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": await response.text()}

    async def query(self, query_text: str, mode: str = "hybrid") -> Dict:
        """
        Submit a query to LightRAG using a selected retrieval mode.
        """
        url = f"{self.base_url}/query"
        payload = {
            "query": query_text,
            "param": {
                "mode": mode
            }
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=self.headers) as response:
                if response.status == 200:
                    return await response.json()
                return {"error": await response.text()}

    async def evaluate_query_modes(self, query_text: str) -> Dict:
        """
        Evaluate the query across multiple LightRAG modes.
        """
        modes = ["naive", "local", "global", "hybrid"]
        results = {}

        for mode in modes:
            result = await self.query(query_text, mode=mode)
            results[mode] = result

        return results
