# 📄 orchestrator.py
# 📍 Location: backend/app/agents/orchestrator.py
# 🧠 Purpose: Central task dispatcher that works with Planner and executes downstream agents

from typing import Dict
from app.routing.semantic_router import semantic_classify
from app.protocol.context import ContextPacket
from app.sockets.telemtry_ws import emit_telemetry_log
from app.core.lightrag_client import LightRAGClient
from semantic_router.schema import RouteChoice
import uuid

class OrchestratorAgent:
    def __init__(self):
        self.session_cache = {}  # Could store recent route traces or intermediate results

    async def handle_task(self, payload: Dict) -> Dict:
        user_input = payload.get("task")
        user_id = payload.get("user_id", str(uuid.uuid4()))

        # Route classification
        route_result: RouteChoice = await semantic_classify(user_input)

        # Construct context
        context = ContextPacket(
            user_id=user_id,
            task=user_input,
            route=route_result.name,
            function_call=route_result.function_call,
        )

        # Emit telemetry for route classification
        await emit_telemetry_log(
            {
                "user_id": user_id,
                "agent": "orchestrator",
                "event": "task_classified",
                "route": route_result.name,
                "function_call": route_result.function_call,
                "task": user_input,
            }
        )

        # Execute RAG query
        lightrag = LightRAGClient()
        rag_result = lightrag.query(user_input)

        # Emit telemetry for LightRAG usage
        await emit_telemetry_log(
            {
                "user_id": user_id,
                "agent": "orchestrator",
                "event": "rag_query",
                "route": route_result.name,
                "task": user_input,
                "source": "LightRAG",
                "rag_result": rag_result,
            }
        )

        return {
            "user_id": user_id,
            "task": user_input,
            "route_used": route_result.name,
            "rag_result": rag_result,
            "context": context.model_dump(),
        }
