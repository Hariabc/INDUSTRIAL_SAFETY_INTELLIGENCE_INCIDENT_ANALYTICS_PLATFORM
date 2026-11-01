import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.routers import (
    health, dashboard, plants, machines, alarms,
    incidents, corrective_actions, anomalies,
    analytics, data_quality, export, settings as sys_settings
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Turning Industrial Safety Events into Actionable Intelligence. Production-grade safety anomaly detection, incident traceability, and evaluation platform.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Enable CORS for local Vite dev and container environments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routers under /api
api_prefix = settings.API_V1_STR

app.include_router(health.router, prefix=api_prefix)
app.include_router(dashboard.router, prefix=api_prefix)
app.include_router(plants.router, prefix=api_prefix)
app.include_router(machines.router, prefix=api_prefix)
app.include_router(alarms.router, prefix=api_prefix)
app.include_router(incidents.router, prefix=api_prefix)
app.include_router(corrective_actions.router, prefix=api_prefix)
app.include_router(anomalies.router, prefix=api_prefix)
app.include_router(analytics.router, prefix=api_prefix)
app.include_router(data_quality.router, prefix=api_prefix)
app.include_router(export.router, prefix=api_prefix)
app.include_router(sys_settings.router, prefix=api_prefix)


@app.get("/")
def root():
    return {
        "platform": settings.PROJECT_NAME,
        "tagline": "Turning Industrial Safety Events into Actionable Intelligence.",
        "documentation": "/docs",
        "api_v1": settings.API_V1_STR,
    }
