from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from backend.app.db import get_db  # your session provider
from backend.app.core.telemetry_models import TelemetryEvent
from typing import List, Optional
from datetime import datetime

router = APIRouter()

@router.get("/api/telemetry_query")
async def query_telemetry(
    agent: Optional[str] = Query(None),
    retrieval_mode: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session_id: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> List[dict]:
    try:
        query = db.query(TelemetryEvent)

        if agent:
            query = query.filter(TelemetryEvent.agent == agent)
        if retrieval_mode:
            query = query.filter(TelemetryEvent.retrieval_mode == retrieval_mode)
        if status:
            query = query.filter(TelemetryEvent.status == status)
        if session_id:
            query = query.filter(TelemetryEvent.session_id == session_id)

        results = query.order_by(TelemetryEvent.timestamp.desc()).limit(100).all()
        return [
            {
                "timestamp": e.timestamp.isoformat(),
                "agent": e.agent,
                "retrieval_mode": e.retrieval_mode,
                "status": e.status,
                "session_id": e.session_id,
                "message": e.message,
            }
            for e in results
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
