from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import init_db
from app.routers.analytics import router as analytics_router
from app.routers.dashboard import router as dashboard_router
from app.routers.logs import router as logs_router
from app.routers.ws import router as ws_router

app = FastAPI(title="LogSight")


@app.on_event("startup")
async def startup():
    init_db()


app.include_router(logs_router)
app.include_router(analytics_router)
app.include_router(dashboard_router)
app.include_router(ws_router)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.get("/")
async def dashboard():
    return FileResponse("app/static/index.html")
