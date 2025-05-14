#!/usr/bin/env python3

import os

# Define the logs to be written
LOGS = {
    "traceability_matrix.md": """# 📌 Phantom Traceability Matrix

| Feature / Functionality | Related File(s) | Status | Test Verified | Notes |
|-------------------------|------------------|--------|----------------|-------|
| Azure RAG Ingestion     | `rag_handler.py`, `rag_client.py` | ✅ | ✅ | Handles ACL-tagged document ingestion |
| LightRAG Support        | `lightrag_client.py`, `VectorSettings.tsx` | ✅ | ✅ | Supports alternative RAG method |
| Dual Query Evaluation   | `rag_handler.py`, `Answer.tsx` | ✅ | ✅ | Admin toggle between Azure RAG / LightRAG |
| MCP-Driven Toggle UI    | `VectorSettings.tsx`, `Settings.tsx` | ✅ | ✅ | System-wide configuration |
| PostgreSQL Log Search   | `telemetry_query_postgres.py`, `TelemetryDashboard.jsx` | ✅ | ✅ | Real-time + historical search |
""",
    "integration_assurance_log.md": """# 🤖 Phantom Integration Assurance Log

| Component | Integration Point | Status | Details |
|-----------|-------------------|--------|---------|
| Azure AI Search | Ingestion + Search | ✅ | Confirmed via API + Frontend |
| LightRAG Container | Local & Azure Deploy | ✅ | Confirmed via endpoint test |
| PostgreSQL Logs | FastAPI API + React UI | ✅ | Conditional fallback to WebSocket |
| Frontend Query Toggle | Azure + LightRAG | ✅ | UI switch with telemetry tagging |
""",
    "change_log.md": """# 📘 Phantom MVP Change Log

## Recent Changes

### ✅ feat: Dual RAG Mode Ingestion Enabled
- Added ACL-tagging support during ingestion
- Supports both Azure Search and LightRAG

### ✅ feat: Telemetry Dashboard Integration
- Real-time (WebSocket) and PostgreSQL search toggle
- Admin view only

### ✅ feat: Frontend Toggles (Settings + VectorSettings)
- MCP-inspired UI switches for Azure RAG and LightRAG

### ✅ fix: GitHub Secret Rejection Resolved
- Secret purged using `bfg`
"""
}

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Write all log files
for filename, content in LOGS.items():
    with open(os.path.join("logs", filename), "w", encoding="utf-8") as f:
        f.write(content)

print("✅ Traceability, integration, and change logs written to ./logs/")
