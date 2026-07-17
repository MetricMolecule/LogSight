import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.ws_manager import manager, redis_listener

router = APIRouter()

listener_started = False


@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    global listener_started

    await manager.connect(websocket)

    if not listener_started:
        asyncio.create_task(redis_listener())
        listener_started = True

    try:
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
