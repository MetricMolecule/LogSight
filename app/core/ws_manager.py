from fastapi import WebSocket

from app.core.redis import redis


class ConnectionManager:
    def __init__(self):
        self.connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.connections:
            self.connections.remove(websocket)

    async def broadcast(self, message: str):
        dead = []

        for connection in self.connections:
            try:
                await connection.send_text(message)
            except Exception:
                dead.append(connection)

        for connection in dead:
            self.disconnect(connection)


manager = ConnectionManager()


async def redis_listener():
    pubsub = redis.pubsub()

    await pubsub.subscribe("logs-live")

    async for message in pubsub.listen():
        if message["type"] != "message":
            continue

        await manager.broadcast(message["data"])
