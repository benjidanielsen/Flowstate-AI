import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List

app = FastAPI()

# Allow CORS for frontend origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # adjust to your frontend url
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/pipeline-updates")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection open, listen for messages if needed
            data = await websocket.receive_text()
            # Echo received message or handle commands if desired
            await manager.send_personal_message(f"Message received: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Example function to broadcast pipeline updates to all clients
async def broadcast_pipeline_update(update: dict):
    message = json.dumps({"type": "pipeline_update", "data": update})
    await manager.broadcast(message)

# Example usage: 
# In your pipeline processing logic, after an update occurs, call:
# await broadcast_pipeline_update({"pipeline_id": 123, "status": "running", "progress": 42})

# To run this server, use:
# uvicorn backend.websocket_server:app --reload
