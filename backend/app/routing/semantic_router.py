#  semantic_router.py
#  Location: backend/app/routing/semantic_router.py
# 易 Purpose: Determine agent route using semantic similarity (LLM embedding) with cache fallback

from typing import Dict, List, Optional
from semantic_router import Route, RouteChoice
from semantic_router.routers import SemanticRouter
from semantic_router.encoders import OpenAIEncoder
from semantic_router.llms import OpenAILLM
from app.config import get_settings
from app.sockets.telemtry_ws import broadcast_telemetry_event
import os
import asyncio
import numpy as np
import time

# Load environment variables
env = get_settings()

# Create OpenAI encoder and LLM
encoder = OpenAIEncoder()
llm = OpenAILLM(name=env.openai_model)

# Define function schemas for dynamic route support
def get_function_schema(name: str, description: str, parameters: Dict) -> Dict:
    return {
        "name": name,
        "description": description,
        "parameters": {
            "type": "object",
            "properties": parameters,
            "required": list(parameters.keys())
        }
    }

# Define Phantom agent routes
routes = [
    Route(
        name="compliance_agent",
        utterances=["check compliance logs", "audit trail for user", "compliance risk"],
        function_schemas=[
            get_function_schema(
                "check_compliance_logs",
                "Returns compliance logs for a given time range",
                {"start_date": {"type": "string"}, "end_date": {"type": "string"}}
            )
        ],
        llm=llm,
        score_threshold=0.75,
        metadata={"agent": "compliance"}
    ),
    Route(
        name="contact_center_agent",
        utterances=["show latest customer issues", "summarize call center tickets"],
        function_schemas=[
            get_function_schema(
                "summarize_contact_issues",
                "Summarizes recent customer service issues",
                {"channel": {"type": "string"}}
            )
        ],
        llm=llm,
        score_threshold=0.75,
        metadata={"agent": "contact_center"}
    ),
    Route(
        name="default",
        utterances=["run a query", "analyze this text"],
        score_threshold=0.5,
        metadata={"agent": "fallback"}
    )
]

# Initialize the Semantic Router
router = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")

# In-memory cache to store embeddings
_embedding_cache: Dict[str, np.ndarray] = {}

async def semantic_classify(task: str) -> RouteChoice:
    """Use SemanticRouter to classify the task and return a RouteChoice."""
    choice = router(task)
    await broadcast_telemetry_event({
        "event": "semantic_route_classification",
        "task": task,
        "selected_route": choice.name,
        "timestamp": time.time()
    })
    return choice

def clear_embedding_cache():
    _embedding_cache.clear()

async def preload_intents():
    for route in routes:
        for utt in route.utterances:
            await get_embedding(utt)

async def get_embedding(text: str) -> np.ndarray:
    """Get embedding for a given text using OpenAI encoder."""
    if text in _embedding_cache:
        return _embedding_cache[text]
    vector = np.array(encoder([text])[0])
    _embedding_cache[text] = vector
    return vector

async def debug_similarity(task: str) -> Dict[str, float]:
    task_vector = await get_embedding(task)
    scores = {}
    for route in routes:
        for utt in route.utterances:
            intent_vector = await get_embedding(utt)
            similarity = np.dot(task_vector, intent_vector) / (
                np.linalg.norm(task_vector) * np.linalg.norm(intent_vector)
            )
            scores[f"{route.name} - {utt}"] = similarity
    return scores
