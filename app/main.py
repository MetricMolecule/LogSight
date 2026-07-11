from fastapi import FastAPI

from app.routers.logs import router as logs_router

app = FastAPI(
    title="LogSight",
    description="Distributed Log Ingestion Platform",
    version="0.1.0",
)

app.include_router(logs_router)


@app.get("/")
async def root():
    return {"message": "Welcome to LogSight!"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
