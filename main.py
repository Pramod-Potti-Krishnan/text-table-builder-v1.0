"""
Text and Table Content Builder v1.0
===================================

Main FastAPI application entry point.

LLM-powered content generation service for presentation slides.
Generates HTML-formatted text and tables with context retention.
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Add current directory to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.routes import router
from app.core.session_manager import get_session_manager


# Load environment variables
load_dotenv()

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "info").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

if LOG_FORMAT == "json":
    # JSON logging for production
    logging.basicConfig(
        level=LOG_LEVEL,
        format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}',
        datefmt="%Y-%m-%d %H:%M:%S"
    )
else:
    # Standard logging for development
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("="*80)
    logger.info("TEXT AND TABLE CONTENT BUILDER v1.0 - STARTING")
    logger.info("="*80)

    # Log configuration
    logger.info(f"LLM Provider: {os.getenv('LLM_PROVIDER', 'gemini')}")
    logger.info(f"LLM Model: {os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')}")
    logger.info(f"Session Storage: {'Redis' if os.getenv('USE_REDIS') == 'true' else 'In-Memory'}")
    logger.info(f"Session TTL: {os.getenv('SESSION_CACHE_TTL', '3600')}s")
    logger.info(f"Word Count Tolerance: ±{float(os.getenv('WORD_COUNT_TOLERANCE', '0.10'))*100}%")

    # Initialize session manager (creates singleton)
    session_manager = get_session_manager()
    logger.info(f"Session manager initialized: {session_manager.store.__class__.__name__}")

    # Verify LLM client can be initialized
    try:
        from app.core.llm_client import get_llm_client, LLMClientFactory

        available_providers = LLMClientFactory.get_available_providers()
        logger.info(f"Available LLM providers: {available_providers}")

        llm_client = get_llm_client()
        logger.info(f"LLM client initialized: {llm_client.__class__.__name__}")

    except Exception as e:
        logger.error(f"Failed to initialize LLM client: {e}")
        logger.warning("Service will start but LLM generation may fail")

    logger.info("="*80)
    logger.info("SERVICE READY")
    logger.info("="*80)

    yield

    # Shutdown
    logger.info("="*80)
    logger.info("TEXT AND TABLE CONTENT BUILDER - SHUTTING DOWN")
    logger.info("="*80)

    # Cleanup expired sessions
    try:
        await session_manager.cleanup_expired_sessions()
        logger.info("Cleaned up expired sessions")
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")

    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Text and Table Content Builder",
    description="""
    LLM-powered content generation service for presentation slides.

    ## Features
    - **Rich HTML Text Generation**: Creates engaging, formatted text with proper semantics
    - **Smart Table Generation**: LLM-optimized table structures from data and descriptions
    - **Context Retention**: Maintains slide history for content flow and coherence
    - **Multi-Provider Support**: Gemini, OpenAI, and Anthropic (configurable)
    - **Word Count Control**: Flexible word count targeting with ±10% tolerance
    - **Session Management**: Presentation-level context tracking

    ## Endpoints
    - `/generate/text` - Generate HTML text content
    - `/generate/table` - Generate HTML table
    - `/generate/batch/text` - Batch text generation
    - `/generate/batch/table` - Batch table generation
    - `/session/{presentation_id}` - Get session info
    - `/health` - Health check

    ## Configuration
    Set via environment variables (see .env.example):
    - `LLM_PROVIDER` - gemini, openai, or anthropic
    - `LLM_MODEL` - Provider-specific model name
    - `SESSION_CACHE_TTL` - Session lifetime in seconds
    - `WORD_COUNT_TOLERANCE` - Acceptable word count variance
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*")
if allowed_origins == "*":
    origins = ["*"]
else:
    origins = [origin.strip() for origin in allowed_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured with origins: {origins}")

# Include API routes
app.include_router(router, prefix="/api/v1")

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint with service information.
    """
    return {
        "service": "Text and Table Content Builder",
        "version": "1.0.0",
        "status": "running",
        "description": "LLM-powered content generation for presentations",
        "endpoints": {
            "api": "/api/v1",
            "docs": "/docs",
            "health": "/health"
        }
    }


# Health check endpoint (Railway compatibility)
@app.get("/health")
async def health_check_root():
    """
    Root-level health check for Railway.

    Railway expects /health endpoint for health checks.
    """
    from app.core.llm_client import get_llm_client

    try:
        llm_client = get_llm_client()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "service": "text-table-builder",
            "llm_provider": llm_client.__class__.__name__.replace("Client", "").lower(),
            "llm_model": llm_client.model
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Main entry point (for testing locally)
if __name__ == "__main__":
    import uvicorn

    PORT = int(os.getenv("PORT", 8001))
    HOST = os.getenv("HOST", "0.0.0.0")
    RELOAD = os.getenv("RELOAD", "false").lower() == "true"

    logger.info(f"Starting server on {HOST}:{PORT} (reload: {RELOAD})")

    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL.lower()
    )
