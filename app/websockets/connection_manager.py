from fastapi import WebSocket
from typing import Dict, List

class ConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, List[WebSocket]] = {}
        self.talleres: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, id_emergencia: int):
        await websocket.accept()
        if id_emergencia not in self.rooms:
            self.rooms[id_emergencia] = []
        self.rooms[id_emergencia].append(websocket)

    def disconnect(self, websocket: WebSocket, id_emergencia: int):
        if id_emergencia in self.rooms:
            self.rooms[id_emergencia].remove(websocket)
            if not self.rooms[id_emergencia]:
                del self.rooms[id_emergencia]

    async def broadcast(self, id_emergencia: int, mensaje: dict):
        if id_emergencia in self.rooms:
            desconectados = []
            for ws in self.rooms[id_emergencia]:
                try:
                    await ws.send_json(mensaje)
                except Exception:
                    desconectados.append(ws)
            for ws in desconectados:
                self.disconnect(ws, id_emergencia)

    async def connect_taller(self, websocket: WebSocket, id_taller: int):
        await websocket.accept()
        if id_taller not in self.talleres:
            self.talleres[id_taller] = []
        self.talleres[id_taller].append(websocket)

    def disconnect_taller(self, websocket: WebSocket, id_taller: int):
        if id_taller in self.talleres:
            self.talleres[id_taller].remove(websocket)
            if not self.talleres[id_taller]:
                del self.talleres[id_taller]

    async def broadcast_taller(self, id_taller: int, mensaje: dict):
        if id_taller in self.talleres:
            desconectados = []
            for ws in self.talleres[id_taller]:
                try:
                    await ws.send_json(mensaje)
                except Exception:
                    desconectados.append(ws)
            for ws in desconectados:
                self.disconnect_taller(ws, id_taller)

manager = ConnectionManager()