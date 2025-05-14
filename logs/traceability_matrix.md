# 📌 Phantom Traceability Matrix

| Feature / Functionality | Related File(s) | Status | Test Verified | Notes |
|-------------------------|------------------|--------|----------------|-------|
| Azure RAG Ingestion     | `rag_handler.py`, `rag_client.py` | ✅ | ✅ | Handles ACL-tagged document ingestion |
| LightRAG Support        | `lightrag_client.py`, `VectorSettings.tsx` | ✅ | ✅ | Supports alternative RAG method |
| Dual Query Evaluation   | `rag_handler.py`, `Answer.tsx` | ✅ | ✅ | Admin toggle between Azure RAG / LightRAG |
| MCP-Driven Toggle UI    | `VectorSettings.tsx`, `Settings.tsx` | ✅ | ✅ | System-wide configuration |
| PostgreSQL Log Search   | `telemetry_query_postgres.py`, `TelemetryDashboard.jsx` | ✅ | ✅ | Real-time + historical search |
