from typing import Dict
from fastapi import WebSocket

class WebSocketManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    def add(self, id: str, websocket: WebSocket) -> WebSocket:
        self.active_connections[id] = websocket
        return websocket

    async def remove(self, id: str):
        websocket = self.active_connections.pop(id, None)
        await websocket.close()

    def get_by_id(self, id: str) -> WebSocket | None:
        return self.active_connections.get(id, None)

websocket_manager = WebSocketManager()