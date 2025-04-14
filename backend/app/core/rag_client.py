# 📄 rag_client.py
# 📍 Location: backend/app/core/rag_client.py
# 🧠 Purpose: Async traditional RAG evaluation using Azure OpenAI (GPT-3.5 / GPT-4)

import time
import aiohttp
from app.config import get_settings

settings = get_settings()

async def query_traditional_rag(prompt: str, model: str = "gpt-3.5-turbo") -> dict:
    """
    Submit a query to Azure OpenAI ChatCompletion endpoint asynchronously.
    Returns dict with model response, latency, token usage.
    """
    start_time = time.time()

    headers = {
        "api-key": settings.openai_api_key,
        "Content-Type": "application/json"
    }

    url = f"{settings.openai_endpoint}/openai/deployments/{settings.openai_deployment}/chat/completions?api-version={settings.openai_api_version}"

    payload = {
        "model": settings.openai_deployment,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 1,
        "n": 1
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                end_time = time.time()
                latency_ms = int((end_time - start_time) * 1000)
                result = await response.json()

                completion = result["choices"][0]["message"]["content"]
                tokens_used = result.get("usage", {}).get("total_tokens", 0)

                return {
                    "rag_response": completion,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                    "llm_model": model
                }

    except Exception as e:
        return {
            "error": str(e),
            "latency_ms": 0,
            "tokens_used": 0,
            "llm_model": model
        }
