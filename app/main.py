from fastapi import FastAPI

from app.routers.analytics import router as analytics_router
from app.routers.logs import router as logs_router

app = FastAPI(
    title="LogSight",
    version="0.1.0",
)

app.include_router(logs_router)
app.include_router(analytics_router)
