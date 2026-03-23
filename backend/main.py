"""
Project Catalyst - Sample Backend API (v1)
FastAPI microservice for testing IDP platform features:
- Istio Ambient Mesh (mTLS, L7 routing, canary)
- Observability (Prometheus metrics, tracing)
- Health checks (liveness, readiness)
"""

import os
import time
import socket
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

APP_VERSION = os.getenv("APP_VERSION", "v1")
APP_COLOR = os.getenv("APP_COLOR", "#2196F3")  # Blue for v1
POD_NAME = os.getenv("HOSTNAME", "unknown")
NODE_NAME = os.getenv("NODE_NAME", "unknown")
NAMESPACE = os.getenv("POD_NAMESPACE", "default")

app = FastAPI(
    title="Project Catalyst API",
    description="Sample microservice for IDP platform testing",
    version=APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulated database (Redis/PostgreSQL test)
REDIS_HOST = os.getenv("REDIS_HOST", "")
DB_HOST = os.getenv("DB_HOST", "")

start_time = time.time()


@app.get("/")
async def root():
    return {
        "service": "project-catalyst-api",
        "version": APP_VERSION,
        "color": APP_COLOR,
        "message": f"Hello from {APP_VERSION}!",
        "pod": POD_NAME,
        "node": NODE_NAME,
        "namespace": NAMESPACE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/version")
async def version():
    """Returns version info - useful for testing traffic splitting."""
    return {
        "version": APP_VERSION,
        "color": APP_COLOR,
        "pod": POD_NAME,
    }


@app.get("/api/info")
async def info(request: Request):
    """Returns detailed info including request headers for Istio testing."""
    headers = dict(request.headers)
    return {
        "service": "project-catalyst-api",
        "version": APP_VERSION,
        "color": APP_COLOR,
        "pod": POD_NAME,
        "node": NODE_NAME,
        "namespace": NAMESPACE,
        "hostname": socket.gethostname(),
        "uptime_seconds": round(time.time() - start_time, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_headers": {
            "host": headers.get("host", ""),
            "x-forwarded-for": headers.get("x-forwarded-for", ""),
            "x-request-id": headers.get("x-request-id", ""),
            "x-envoy-decorator-operation": headers.get("x-envoy-decorator-operation", ""),
            "x-version": headers.get("x-version", ""),
            "x-test-user": headers.get("x-test-user", ""),
        },
    }


@app.get("/api/items")
async def list_items():
    """Sample CRUD endpoint."""
    return {
        "items": [
            {"id": 1, "name": "Platform Catalyst", "status": "active"},
            {"id": 2, "name": "EKS Cluster", "status": "running"},
            {"id": 3, "name": "Istio Mesh", "status": "healthy"},
        ],
        "version": APP_VERSION,
        "total": 3,
    }


@app.get("/api/items/{item_id}")
async def get_item(item_id: int):
    """Sample item endpoint."""
    items = {
        1: {"id": 1, "name": "Platform Catalyst", "status": "active"},
        2: {"id": 2, "name": "EKS Cluster", "status": "running"},
        3: {"id": 3, "name": "Istio Mesh", "status": "healthy"},
    }
    item = items.get(item_id)
    if not item:
        return JSONResponse(status_code=404, content={"error": "Item not found"})
    return {"item": item, "version": APP_VERSION}


@app.get("/health")
async def health():
    """Liveness probe - is the process running?"""
    return {"status": "healthy", "version": APP_VERSION}


@app.get("/ready")
async def ready():
    """Readiness probe - is the service ready to accept traffic?"""
    return {"status": "ready", "version": APP_VERSION, "uptime": round(time.time() - start_time, 2)}


@app.get("/api/delay/{seconds}")
async def delay(seconds: int):
    """Simulate slow response - useful for testing timeouts and retries."""
    if seconds > 30:
        seconds = 30
    time.sleep(seconds)
    return {
        "message": f"Responded after {seconds}s delay",
        "version": APP_VERSION,
    }


@app.get("/api/status/{code}")
async def status_code(code: int):
    """Return specific HTTP status code - useful for testing circuit breakers."""
    return JSONResponse(
        status_code=code,
        content={
            "requested_status": code,
            "version": APP_VERSION,
            "pod": POD_NAME,
        },
    )


@app.get("/api/headers")
async def show_headers(request: Request):
    """Show all request headers - useful for verifying Istio header manipulation."""
    return {
        "headers": dict(request.headers),
        "version": APP_VERSION,
    }


@app.get("/metrics")
async def metrics():
    """Simple Prometheus-compatible metrics endpoint."""
    uptime = round(time.time() - start_time, 2)
    return Response(
        content=(
            f'# HELP app_info Application info\n'
            f'# TYPE app_info gauge\n'
            f'app_info{{version="{APP_VERSION}",pod="{POD_NAME}"}} 1\n'
            f'# HELP app_uptime_seconds Application uptime\n'
            f'# TYPE app_uptime_seconds gauge\n'
            f'app_uptime_seconds{{version="{APP_VERSION}"}} {uptime}\n'
        ),
        media_type="text/plain",
    )
