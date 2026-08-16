from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.core.logger import configure_logger
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.study_material import router as study_material_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logger()
    logger.info("CampusMind AI backend started")

    yield

    logger.info("CampusMind AI backend stopped")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AI-powered study assistant",
    lifespan=lifespan,
)


# ==========================================
# CORS Middleware
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Routers
# ==========================================

app.include_router(
    health_router,
    prefix=settings.API_PREFIX,
    tags=["Health"],
)

app.include_router(
    auth_router,
    prefix=settings.API_PREFIX,
    tags=["Authentication"],
)

app.include_router(
    study_material_router,
    prefix=settings.API_PREFIX,
    tags=["Study Materials"],
)


# ==========================================
# Root Endpoint
# ==========================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} API is running",
        "version": settings.VERSION,
    }