from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.routers.analytics import router as analytics_router
from app.routers.logs import router as logs_router
from app.routers.ws import router as ws_router

app = FastAPI(
    title="LogSight",
    version="0.1.0",
)

# Serve css/js/images
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static",
)


@app.get("/")
async def home():
    return FileResponse("app/static/index.html")


app.include_router(logs_router)
app.include_router(analytics_router)
app.include_router(ws_router)
