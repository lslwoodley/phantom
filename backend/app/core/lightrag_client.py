# core/lightrag_client.py

import os
import httpx

LIGHTRAG_API_BASE = os.getenv("LIGHTRAG_API_BASE", "http://localhost:8080")

async def query_lightrag(text: str, mode: str = "mix", top_k: int = 10):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{LIGHTRAG_API_BASE}/api/query",
            json={"query": text, "mode": mode, "top_k": top_k}
        )
        response.raise_for_status()
        return response.json()
