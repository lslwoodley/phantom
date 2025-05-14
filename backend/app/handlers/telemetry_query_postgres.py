# backend/app/handlers/telemetry_query_postgres.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime, timedelta
from sqlmodel import select

from app.db import get_session
from app.models.telemetry_models import TelemetryLog
from app.auth.role_required import EntraRBAC

router = APIRouter()

@router.get("/telemetry_query")
def telemetry_query(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    days: Optional[int] = Query(default=7, description="Days back from now to search"),
    limit: Optional[int] = Query(default=25, le=100),
    offset: Optional[int] = Query(default=0),
    claims: dict = Depends(EntraRBAC())
):
    """
    Fetch historical telemetry logs from PostgreSQL with filter support.
    Falls back gracefully if Postgres is not configured.
    """
    try:
        with get_session() as session:
            query = select(TelemetryLog)

            if user_id:
                query = query.where(TelemetryLog.user_id == user_id)
            if status:
                query = query.where(TelemetryLog.status == status)
            if days:
                since = datetime.utcnow() - timedelta(days=days)
                query = query.where(TelemetryLog.timestamp >= since)

            total = session.exec(query).count()
            query = query.offset(offset).limit(limit)

            logs = session.exec(query).all()
            return {
                "filters": {
                    "user_id": user_id,
                    "status": status,
                    "days": days
                },
                "total": total,
                "count": len(logs),
                "results": [log.dict() for log in logs]
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database unavailable or error occurred: {str(e)}")
