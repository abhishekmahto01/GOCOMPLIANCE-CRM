from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin_permissions, auth, employees, health, lookup, operations, sales
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Main Backend API for Gocompliances CRM",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(
    health.router,
    prefix=settings.API_PREFIX,
    tags=["Health"],
)
app.include_router(
    auth.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    employees.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    lookup.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    admin_permissions.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    sales.router,
    prefix=settings.API_PREFIX,
)
app.include_router(
    operations.router,
    prefix=settings.API_PREFIX,
)

