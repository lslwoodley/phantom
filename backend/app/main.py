#  main.py
#  Location: backend/app/main.py
# 易 Purpose: FastAPI entrypoint for Phantom — orchestrates task handling, classification, route execution, and route evaluation

from fastapi import FastAPI, WebSocket, Request, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.agents.orchestrator import OrchestratorAgent
from app.agents.planner import PlannerAgent
from app.config import get_settings
from app.core.lighrag_client import LightRAGClient
from app.core.rag_client import query_traditional_rag
from app.utils.blob_logger import upload_telemetry_to_blob, list_telemetry_logs, get_telemetry_log
from app.db import get_session
from app.models.telemetry_model import TelemetryLog
from app.auth.msal_auth import EntraRBAC
from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.handlers import telemetry_query_postgres


import json
import uuid
import os
import asyncio
from typing import Optional, List

app = FastAPI(title="Phantom AI Platform", version="0.1.0")
app.include_router(telemetry_query_postgres.router)

# Load settings
env = get_settings()

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instantiate services
orchestrator = OrchestratorAgent()
planner = PlannerAgent()
lightrag_client = LightRAGClient()

@app.get("/")
def health_check():
    return {"status": "Phantom backend is live"}

@app.post("/task")
async def handle_task(request: Request, claims: dict = Depends(EntraRBAC())):
    payload = await request.json()
    try:
        response = await orchestrator.handle_task(payload)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/classify")
async def classify_task(request: Request, claims: dict = Depends(EntraRBAC())):
    payload = await request.json()
    try:
        result = await planner.classify_and_suggest_routes(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
async def execute_route(request: Request, claims: dict = Depends(EntraRBAC())):
    payload = await request.json()
    try:
        result = await planner.execute_selected_route(payload)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compare_routes")
async def compare_routes(request: Request, claims: dict = Depends(EntraRBAC())):
    payload = await request.json()
    query_text = payload.get("query")
    user_id = payload.get("user_id", str(uuid.uuid4()))

    if not query_text:
        raise HTTPException(status_code=400, detail="Missing query text")

    try:
        with get_session() as session:
            recent = datetime.utcnow() - timedelta(minutes=2)
            duplicate = session.exec(
                select(TelemetryLog).where(
                    TelemetryLog.user_id == user_id,
                    TelemetryLog.query == query_text,
                    TelemetryLog.timestamp >= recent
                )
            ).first()
            if duplicate:
                return {"message": "Duplicate query detected", "duplicate": duplicate.dict()}

        light_comparison = await lighrag_client.evaluate_query_modes(query_text)
        traditional_comparison = await query_traditional_rag(query_text, model="gpt-3.5-turbo")

        routing_scores = {
            "light_rag": {
                "mode_scores": {mode: (1 if result.get("query") else 0) for mode, result in light_comparison.items()}
            },
            "traditional_rag": {
                "confidence": traditional_comparison.get("tokens_used", 0)
            }
        }

        telemetry_data = {
            "user_id": user_id,
            "query": query_text,
            "timestamp": datetime.utcnow().isoformat(),
            "light_rag": light_comparison,
            "traditional_rag": traditional_comparison,
            "status": "completed",
            "routing_scores": routing_scores
        }

        upload_telemetry_to_blob(telemetry_data, user_id)

        db_log = TelemetryLog(
            user_id=user_id,
            query=query_text,
            light_rag=light_comparison,
            traditional_rag=traditional_comparison,
            routing_scores=routing_scores,
            status="completed"
        )
        with get_session() as session:
            session.add(db_log)
            session.commit()

        return telemetry_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_compare_routes")
async def batch_compare_routes(request: Request, claims: dict = Depends(EntraRBAC())):
    payload = await request.json()
    queries = payload.get("queries", [])
    user_id = payload.get("user_id", str(uuid.uuid4()))

    if not queries:
        raise HTTPException(status_code=400, detail="Missing list of queries")

    async def evaluate_one(query_text: str):
        light_result = await lighrag_client.evaluate_query_modes(query_text)
        traditional_result = await query_traditional_rag(query_text, model="gpt-3.5-turbo")

        routing_scores = {
            "light_rag": {
                "mode_scores": {mode: (1 if result.get("query") else 0) for mode, result in light_result.items()}
            },
            "traditional_rag": {
                "confidence": traditional_result.get("tokens_used", 0)
            }
        }

        result = {
            "user_id": user_id,
            "query": query_text,
            "light_rag": light_result,
            "traditional_rag": traditional_result,
            "routing_scores": routing_scores,
            "timestamp": datetime.utcnow().isoformat(),
            "status": "completed"
        }

        upload_telemetry_to_blob(result, user_id)

        db_log = TelemetryLog(
            user_id=user_id,
            query=query_text,
            light_rag=light_result,
            traditional_rag=traditional_result,
            routing_scores=routing_scores,
            status="completed"
        )
        with get_session() as session:
            session.add(db_log)
            session.commit()

        return result

    try:
        results = await asyncio.gather(*(evaluate_one(q) for q in queries))
        return {
            "user_id": user_id,
            "query_count": len(queries),
            "results": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/telemetry_query")
def telemetry_query(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    days: Optional[int] = Query(default=7, description="Days back from now to search"),
    limit: Optional[int] = Query(default=25, le=100),
    offset: Optional[int] = Query(default=0),
    claims: dict = Depends(EntraRBAC())
):
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
        raise HTTPException(status_code=500, detail=str(e))
