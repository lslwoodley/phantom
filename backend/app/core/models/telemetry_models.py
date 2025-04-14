# 📄 telemetry_model.py
# 📍 Location: backend/app/models/telemetry_model.py
# 🧠 Purpose: Define SQLModel structure for storing telemetry in PostgreSQL

from sqlmodel import SQLModel, Field
from typing import Optional, Dict
from datetime import datetime
import uuid

class TelemetryLog(SQLModel, table=True):
    __tablename__ = "telemetry_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    query: str
    status: str = Field(default="completed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    light_rag: Optional[Dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    traditional_rag: Optional[Dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})
    routing_scores: Optional[Dict] = Field(default=None, sa_column_kwargs={"type_": "JSONB"})

# Example DB initialization script:
# from sqlmodel import SQLModel, create_engine
# engine = create_engine("postgresql://user:password@host:port/db")
# SQLModel.metadata.create_all(engine)