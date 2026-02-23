"""
ED CT Brain Workflow System - Main Application Entry Point
Hospital Shah Alam - Emergency Department CT Brain Imaging
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.config import settings
from src.database import init_db, close_db
from src.api.routes import (
    auth_router,
    patients_router,
    scans_router,
    users_router,
    resources_router,
    faq_router,
    dashboard_router,
)
from src.api.websocket import socket_manager, websocket_endpoint


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    await init_db()
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
app = FastAPI(
    title="ED CT Brain Workflow System",
    description="Multi-Agent AI System for Emergency Department CT Brain Imaging Workflow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(scans_router, prefix="/api/v1/scans", tags=["CT Scans"])
app.include_router(users_router, prefix="/api/v1/users", tags=["Users"])
app.include_router(resources_router, prefix="/api/v1/resources", tags=["Resources"])
app.include_router(faq_router, prefix="/api/v1/faq", tags=["FAQ"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])

# WebSocket endpoint
app.add_api_websocket_route("/ws", websocket_endpoint)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "ED CT Brain Workflow System API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "ED CT Brain Workflow System",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)