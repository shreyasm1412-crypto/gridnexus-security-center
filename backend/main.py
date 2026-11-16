from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import os
from .api.persistent import router as persistent_router
from .services.persistent_service import initialize

@asynccontextmanager
async def lifespan(app):
    initialize()
    yield

from .models.schemas import HealthResponse
from .api import (
    dashboard_router,
    grid_router,
    simulation_router,
    alerts_router,
    incidents_router,
)

app = FastAPI(
    lifespan=lifespan,
    title="GridNexus AI — Smart Grid Cyber Defense Backend",
    description=(
        "Software-only smart grid cybersecurity simulation and AI threat detection platform. "
        "Provides digital twin telemetry, multi-layer hybrid threat detection (Rule Engine + "
        "Isolation Forest + Random Forest), risk scoring, alert management, and incident response."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS to support local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("GRIDNEXUS_ALLOWED_ORIGINS", "http://localhost:8080,http://127.0.0.1:8080").split(","),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoint
@app.get("/api/health", response_model=HealthResponse, tags=["Health"])
def health_check() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.now().isoformat(),
        models_loaded=__import__("backend.state", fromlist=["anomaly_detector"]).anomaly_detector.is_trained and __import__("backend.state", fromlist=["attack_classifier"]).attack_classifier.is_trained,
    )

# Root redirect to OpenAPI Swagger documentation
@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/docs")

# Mount API Routers
app.include_router(persistent_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
