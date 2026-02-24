"""FastAPI App Entry Point"""
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.mediroute_router import router
from routers.mediroute_streaming_router import router as streaming_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    logger.info("MediRoute AI service started successfully")
    yield
    logger.info("MediRoute AI service shutting down...")

app = FastAPI(
    title="MediRoute AI",
    description="Autonomous Medical Evacuation Decision Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default port
        "http://localhost:8080",  # Python http.server
        "http://127.0.0.1:8080",
        "http://127.0.0.1:3000",
        "null",  # For file:// protocol (local HTML files)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(streaming_router)

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"status": "ok", "service": "MediRoute AI"}
