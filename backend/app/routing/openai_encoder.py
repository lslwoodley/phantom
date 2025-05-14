# 📄 openai_encoder.py
# 📍 Location: backend/app/routing/openai_encoder.py
# 🧠 Purpose: Centralized OpenAI encoder and LLM wrapper for use in Phantom routing

from semantic_router.encoders import OpenAIEncoder as _OpenAIEncoder
from semantic_router.llms.zure import AzureOpenAILLM
from app.config import get_settings

env = get_settings()

class OpenAIEncoder:
    def __init__(self):
        self.encoder = _OpenAIEncoder(model=env.openai_embedding_deployment)

    def __call__(self, texts):
        return self.encoder(texts)

class OpenAILLM:
    def __init__(self, name: str = None):
        self.llm = AzureOpenAILLM(
            endpoint=env.openai_endpoint,
            api_version=env.openai_api_version,
            model=name or env.openai_model,
        )

    def __call__(self, prompt: str) -> str:
        return self.llm(prompt)
