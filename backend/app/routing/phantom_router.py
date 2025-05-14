# 📄 phantom_router.py
# 📍 Location: backend/app/routing/phantom_router.py
# 🧠 Purpose: Decide which Phantom agent handles a task via semantic-router.

from __future__ import annotations

import asyncio
import time
from typing import Dict, List, Optional

import numpy as np
from semantic_router import Route
from semantic_router.routers import SemanticRouter
from semantic_router.schema import RouteChoice

from backend.app.config import get_settings
from backend.app.routing.openai_encoder import OpenAIEncoder, OpenAILLM  # ✅ wrapper LLM
from backend.app.sockets.telemtry_ws import broadcast_telemetry         # ✅ correct import

# Alias to keep old helper name used elsewhere
broadcast_telemetry_event = broadcast_telemetry

# ────────────────────────────────────────────────────────────────────────
# 🔧 Environment and model instances
# ────────────────────────────────────────────────────────────────────────
env = get_settings()

encoder = OpenAIEncoder()                          # text embeddings
llm     = OpenAILLM(name=env.openai_deployment)    # Azure OpenAI chat LLM

# ────────────────────────────────────────────────────────────────────────
# 🛠️ Helper: build JSON-schema for dynamic routes
# ────────────────────────────────────────────────────────────────────────
def make_schema(name: str, description: str, parameters: Dict) -> Dict:
    return {
        "name":        name,
        "description": description,
        "parameters": {
            "type":       "object",
            "properties": parameters,
            "required":   list(parameters.keys()),
        },
    }

# ────────────────────────────────────────────────────────────────────────
# 🚦 Route definitions
# ────────────────────────────────────────────────────────────────────────
routes: List[Route] = [
    Route(
        name="compliance_agent",
        utterances=[
            "check compliance logs",
            "audit trail for user",
            "compliance risk",
        ],
        function_schemas=[
            make_schema(
                "check_compliance_logs",
                "Return compliance logs within a time range",
                {
                    "start_date": {"type": "string"},
                    "end_date":   {"type": "string"},
                },
            )
        ],
        llm=llm,
        score_threshold=0.75,
        metadata={"agent": "compliance"},
    ),
    Route(
        name="contact_center_agent",
        utterances=[
            "show latest customer issues",
            "summarize call center tickets",
        ],
        function_schemas=[
            make_schema(
                "summarize_contact_issues",
                "Summarize recent customer service issues",
                {"channel": {"type": "string"}},
            )
        ],
        llm=llm,
        score_threshold=0.75,
        metadata={"agent": "contact_center"},
    ),
    Route(  # fallback
        name="default",
        utterances=[
            "run a query",
            "analyze this text",
        ],
        score_threshold=0.5,
        metadata={"agent": "fallback"},
    ),
]

# Build router (local index for speed)
router = SemanticRouter(encoder=encoder, routes=routes, auto_sync="local")

# ────────────────────────────────────────────────────────────────────────
# 🚀 Public helpers
# ────────────────────────────────────────────────────────────────────────
_embedding_cache: Dict[str, np.ndarray] = {}


async def semantic_classify(
    task: str,
    *,
    route_filter: Optional[List[str]] = None,
) -> RouteChoice:
    """
    Classify *task*; return chosen `RouteChoice`.
    If `route_filter` is supplied, only those routes are considered.
    """
    choice: RouteChoice = router(task, route_filter=route_filter)

    # Fire-and-forget telemetry
    asyncio.create_task(
        broadcast_telemetry_event(
            {
                "event":          "semantic_route_classification",
                "task":           task,
                "selected_route": choice.name,
                "route_filter":   route_filter or [],
                "timestamp":      time.time(),
            }
        )
    )
    return choice


def clear_embedding_cache() -> None:
    _embedding_cache.clear()


async def preload_intents() -> None:
    """Warm-up: cache embeddings for every utterance."""
    for r in routes:
        for utt in r.utterances:
            await _get_embedding(utt)

# ────────────────────────────────────────────────────────────────────────
# 🔍 Debug helpers
# ────────────────────────────────────────────────────────────────────────
async def _get_embedding(text: str) -> np.ndarray:
    if text in _embedding_cache:
        return _embedding_cache[text]
    vec = np.array(encoder([text])[0])
    _embedding_cache[text] = vec
    return vec


async def debug_similarity(task: str) -> Dict[str, float]:
    task_vec = await _get_embedding(task)
    scores: Dict[str, float] = {}
    for r in routes:
        for utt in r.utterances:
            intent_vec = await _get_embedding(utt)
            sim = float(
                np.dot(task_vec, intent_vec)
                / (np.linalg.norm(task_vec) * np.linalg.norm(intent_vec))
            )
            scores[f"{r.name} :: {utt}"] = sim
    return scores
