# handlers/rag_handler.py

from fastapi import APIRouter, Request
from services.rag_service import RAGService
from core.lightrag_client import query_lightrag
from auth.graph_utils import GraphHelper
from telemetry_logger import log_telemetry
from jose import jwt
import os
import time

router = APIRouter()

@router.post("/rag/search")
async def secure_rag_search(request: Request):
    body = await request.json()
    query = body.get("query")
    modes = body.get("modes", [])  # expects list: ["azure_rag", "light_rag"]
    bearer_token = request.headers.get("authorization").replace("Bearer ", "")

    claims = jwt.get_unverified_claims(bearer_token)
    oid = claims.get("oid")

    graph = GraphHelper(
        tenant_id=os.getenv("PHANTOM_TENANT_ID"),
        client_id=os.getenv("PHANTOM_APP_CLIENT_ID"),
        client_secret=os.getenv("PHANTOM_APP_SECRET")
    )
    expanded_groups = graph.expand_groups(oid)

    filter_parts = []
    if oid:
        filter_parts.append(f"oids/any(g: g eq '{oid}')")
    if expanded_groups:
        groups_csv = ",".join(f"'{g}'" for g in expanded_groups)
        filter_parts.append(f"groups/any(g: search.in(g, '{groups_csv}'))")
    filter_parts.append("isPublic eq true")
    security_filter = " or ".join(filter_parts)

    results_payload = {}

    if "azure_rag" in modes:
        start = time.time()
        service = RAGService()
        azure_results = await service.secure_search(query_text=query, filter_str=security_filter)
        results_payload["azure_rag"] = azure_results
        log_telemetry({
            "query": query,
            "oid": oid,
            "mode": "azure_rag",
            "filter": security_filter,
            "latency_ms": int((time.time() - start) * 1000),
            "results": [r.get("id", "unknown") for r in azure_results]
        })

    if "light_rag" in modes:
        start = time.time()
        light_results = await query_lightrag(query, mode="mix")
        results_payload["light_rag"] = light_results
        log_telemetry({
            "query": query,
            "oid": oid,
            "mode": "light_rag",
            "filter": "N/A",
            "latency_ms": int((time.time() - start) * 1000),
            "results": [r.get("doc_id", "unknown") for r in light_results.get("results", [])]
        })

    return {
        "query": query,
        "modes_used": modes,
        "results": results_payload,
        "user": oid
    }
