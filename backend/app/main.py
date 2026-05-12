"""
RecruitIQ — FastAPI Application Entry Point
"""
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import analysis, auth, export, jobs, resume
from app.core.config import get_settings
from app.core.database import init_db
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RecruitIQ", version=settings.app_version)
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down RecruitIQ")


app = FastAPI(
    title="RecruitIQ API",
    description=(
        "AI-powered resume to job match intelligence platform. "
        "Analyzes semantic match, extracts skills, generates learning roadmaps, "
        "and prepares tailored interview questions."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = round((time.perf_counter() - start) * 1000, 2)
    logger.info(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=elapsed,
    )
    return response


# ── Routes ───────────────────────────────────────────────────────────────────

app.include_router(auth.router, prefix="/api/v1")
app.include_router(resume.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(export.router, prefix="/api/v1")


@app.get("/health", tags=["meta"])
def health_check():
    return {"status": "ok", "version": settings.app_version}


@app.get("/", tags=["meta"])
def root():
    return {
        "name": "RecruitIQ",
        "version": settings.app_version,
        "docs": "/docs",
    }
