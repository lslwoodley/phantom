# 📍 backend/app/sockets/telemetry_ws.py
from fastapi import WebSocket, APIRouter
from typing import List

router = APIRouter()
connections: List[WebSocket] = []

@router.websocket("/ws/telemetry")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception as e:
        connections.remove(websocket)

async def broadcast_telemetry(message: dict):
    removable_connections = []
    for connection in connections:
        try:
            await connection.send_json(message)
        except:
            removable_connections.append(connection)
    for conn in removable_connections:
        connections.remove(conn)
