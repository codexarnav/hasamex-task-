"""Main FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import (
    InsightOSError,
    NotFoundError,
    ParsingError,
    LLMError,
    EmbeddingError,
    VectorStoreError,
    ProjectIsolationError,
    InsufficientEvidenceError,
    FileStorageError,
    AnalysisError,
)
from app.api.v1.router import api_v1_router
from app.retrieval.qdrant import get_qdrant_repository

settings = get_settings()
setup_logging(debug=settings.DEBUG)
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan management."""
    logger.info("Starting InsightOS Backend V1...", extra={"operation": "startup"})
    try:
        # Attempt Qdrant collection initialization on startup (tolerant if offline during unit tests)
        qdrant_repo = get_qdrant_repository()
        await qdrant_repo.init_collection()
    except Exception as e:
        logger.warning(
            f"Qdrant collection initialization deferred or unreachable: {e}",
            extra={"operation": "startup_qdrant"},
        )
    yield
    logger.info("InsightOS Backend shutdown completed.", extra={"operation": "shutdown"})


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="InsightOS - AI-Powered Qualitative Research Intelligence Platform V1",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_v1_router)


# Global Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_exception_handler(request: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(ProjectIsolationError)
async def isolation_exception_handler(request: Request, exc: ProjectIsolationError):
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(ParsingError)
async def parsing_exception_handler(request: Request, exc: ParsingError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(LLMError)
async def llm_exception_handler(request: Request, exc: LLMError):
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(VectorStoreError)
async def vector_exception_handler(request: Request, exc: VectorStoreError):
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(AnalysisError)
async def analysis_exception_handler(request: Request, exc: AnalysisError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.exception_handler(InsightOSError)
async def general_insightos_exception_handler(request: Request, exc: InsightOSError):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": exc.message, "detail": exc.detail},
    )


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    """Health check endpoint for cloud hosting providers."""
    return {"status": "ok"}

