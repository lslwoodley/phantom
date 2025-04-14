#  context.py
#  Location: backend/app/protocol/context.py
# 易 Purpose: Defines the shared Model Context Protocol (MCP) object used by all Phantom agents

from typing import Optional, Dict, Any
from pydantic import BaseModel

class ContextPacket(BaseModel):
    user_id: str
    task: str
    classification: Dict[str, Any]  # agent, llm, cost, etc.
    access_token: Optional[str] = None
    snapshot: Optional[Dict[str, Any]] = None  # MSGraph snapshot or LightRAG memory
    metadata: Optional[Dict[str, Any]] = {}  # e.g., timestamp, agent source, tags

    def summary(self):
        return {
            "user": self.user_id,
            "agent": self.classification.get("agent"),
            "llm": self.classification.get("llm"),
            "tags": self.metadata.get("tags", []),
            "with_snapshot": self.snapshot is not None
        }
