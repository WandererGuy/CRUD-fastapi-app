from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import init_redis, close_redis


# ---------- Application Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.

    Handles startup and shutdown events:
    - Startup: Initialize Redis connection pool
    - Shutdown: Close Redis connection pool
    """
    # Startup
    await init_redis()
    yield
    # Shutdown
    await close_redis()


# ---------- Initialize ----------
app = FastAPI(
    title="Brand CRUD API with JWT Authentication",
    lifespan=lifespan
)


# ---------- Include Routers ----------
from routes.v1.brand import router as brand_router
from routes.v1.auth import router as auth_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(brand_router, prefix="/api/v1")


# ---------- Root Endpoint ----------
@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Brand CRUD API with JWT Authentication",
        "version": "1.0.0",
        "status": "active"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)