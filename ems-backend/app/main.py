# FastAPI is the web framework we use to build the REST API.
# It handles incoming HTTP requests and routes them to the right functions.
from fastapi import FastAPI

# CORSMiddleware handles Cross-Origin Resource Sharing (CORS).
# Browsers block requests made from one origin (e.g. localhost:5173) to a
# different origin (e.g. localhost:8000) unless the server explicitly allows it.
# This middleware adds the required HTTP headers so the frontend can talk to the API.
from fastapi.middleware.cors import CORSMiddleware

# Import each router module. Each router groups related endpoints together
# (e.g. all authentication routes live in auth.router).
from app.routers import auth, devices, telemetry, alerts, reports, users, buildings

# Create the main FastAPI application instance.
# The title, description, and version appear in the auto-generated API docs
# at http://localhost:8000/docs (Swagger UI) and /redoc.
app = FastAPI(
    title="IEMS API",
    description="Intelligent Energy Management System API",
    version="1.0.0"
)

# Allow requests from the frontend dev server (Vite runs on port 5173 by default).
# Without this, the browser would refuse to send API requests from the frontend.
app.add_middleware(
    CORSMiddleware,
    # List of frontend origins that are allowed to make requests to this API.
    # Add your production domain here before deploying (e.g. "https://myapp.com").
    allow_origins=["http://localhost:5173"],
    # Allow cookies and Authorization headers to be included in cross-origin requests.
    # Required for JWT token-based authentication to work from the browser.
    allow_credentials=True,
    # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.).
    allow_methods=["*"],
    # Allow all request headers (e.g. Content-Type, Authorization).
    allow_headers=["*"],
)

# --- Register Routers ---
# Each router is a mini-application that handles one group of related endpoints.
# `prefix` sets the URL path that all routes in that router will start with.
# `tags` groups the routes together in the auto-generated /docs page.

app.include_router(auth.router,      prefix="/api/v1/auth",      tags=["Authentication"])
app.include_router(users.router,     prefix="/api/v1/users",     tags=["Users"])
app.include_router(buildings.router, prefix="/api/v1/buildings", tags=["Buildings"])
app.include_router(devices.router,   prefix="/api/v1/devices",   tags=["Devices"])
app.include_router(telemetry.router, prefix="/api/v1/telemetry", tags=["Telemetry"])
app.include_router(alerts.router,    prefix="/api/v1/alerts",    tags=["Alerts"])
app.include_router(reports.router,   prefix="/api/v1/reports",   tags=["Reports"])


# Health-check endpoint — a simple route that returns {"status": "ok"}.
# Uptime monitors, load balancers, and Docker health checks call this URL
# to verify the API process is running and responding to requests.
# Try it at: http://localhost:8000/health
@app.get("/health")
def health_check():
    return {"status": "ok", "service": "IEMS API"}