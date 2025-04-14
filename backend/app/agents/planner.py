# 📍 backend/app/agents/planner.py
from app.core.lightrag_client import LightRAGClient
from app.core.msgraph_client import MSGraphClient
from app.routing.semantic_router import semantic_classify
from app.sockets.telemetry_ws import broadcast_telemetry
from app.protocol.context import ContextPacket
from typing import Dict
import uuid
import datetime

class PlannerAgent:
    def __init__(self):
        self.memory_index = {}  # user-specific context memory

    async def classify_and_suggest_routes(self, payload: Dict) -> Dict:
        user_input = payload.get("task")
        user_id = payload.get("user_id", str(uuid.uuid4()))
        user_token = payload.get("access_token")

        # Semantic classification (LLM-powered)
        route_choice = await semantic_classify(user_input)

        # MSGraph context ingestion
        graph_client = MSGraphClient(user_token)
        context_snapshot = graph_client.snapshot_user_context()

        # Store context in memory
        self.memory_index[user_id] = context_snapshot

        telemetry_event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "user_id": user_id,
            "task": user_input,
            "route": route_choice.name,
            "fallback_used": route_choice.name == "default",
            "context_ingested": True,
            "source": "SemanticRouter",
        }

        # Broadcast telemetry immediately
        await broadcast_telemetry(telemetry_event)

        return {
            "user_id": user_id,
            "task": user_input,
            "route_choice": route_choice.dict(),
            "context": context_snapshot,
        }

    async def execute_selected_route(self, payload: Dict) -> Dict:
        user_id = payload.get("user_id")
        query = payload.get("task")
        selected_route = payload.get("route")

        lightrag = LightRAGClient()
        rag_result = lightrag.query(query)

        telemetry_event = {
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "user_id": user_id,
            "task": query,
            "route": selected_route,
            "rag_used": True,
            "source": "LightRAG",
            "rag_result_summary": rag_result.get("summary", "No summary"),
        }

        # Broadcast RAG usage telemetry
        await broadcast_telemetry(telemetry_event)

        return {
            "user_id": user_id,
            "route_used": selected_route,
            "rag_result": rag_result,
        }
