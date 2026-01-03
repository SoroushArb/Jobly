from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.routers import (
    profile_router,
    jobs_router,
    matches_router,
    packets_router,
    interview_router,
    applications_router,
    prefill_router,
    cvs_router,
    events_router,
    background_jobs_router,
)
from app.models import Database
from app.config import config
from app.middleware import (
    RequestIDMiddleware,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

# Validate environment at startup
config.validate_or_exit()

app = FastAPI(
    title="Jobly API",
    description="AI Job Hunter Agent - Profile Management, Job Ingestion, Matching, Interview Prep & Application Tracking",
    version="7.0.0"
)

# Add request ID middleware
app.add_middleware(RequestIDMiddleware)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(profile_router)
app.include_router(cvs_router)
app.include_router(jobs_router)
app.include_router(matches_router)
app.include_router(packets_router)
app.include_router(interview_router)
app.include_router(applications_router)
app.include_router(prefill_router)
app.include_router(events_router)
app.include_router(background_jobs_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    logger.info("Starting Jobly API...")
    Database.get_client()
    logger.info("Database connection initialized")
    
    # Create indexes for performance
    await create_indexes()


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    logger.info("Shutting down Jobly API...")
    await Database.close()
    logger.info("Database connection closed")


async def create_indexes():
    """Create database indexes for performance"""
    try:
        db = Database.get_database()
        
        # TTL for events collection (7 days)
        EVENTS_TTL_SECONDS = 604800  # 7 days in seconds
        
        # Background jobs indexes
        jobs_col = db["background_jobs"]
        await jobs_col.create_index([("status", 1), ("created_at", 1)])
        await jobs_col.create_index([("user_id", 1), ("created_at", -1)])
        await jobs_col.create_index([("type", 1)])
        
        # Jobs indexes
        jobs_db_col = db["jobs"]
        await jobs_db_col.create_index([("content_hash", 1)], unique=True)
        await jobs_db_col.create_index([("posted_date", -1)])
        await jobs_db_col.create_index([("remote_type", 1)])
        
        # Matches indexes
        matches_col = db["matches"]
        await matches_col.create_index([("profile_id", 1), ("score_total", -1)])
        await matches_col.create_index([("job_id", 1)])
        
        # Packets indexes
        packets_col = db["packets"]
        await packets_col.create_index([("profile_id", 1), ("created_at", -1)])
        await packets_col.create_index([("job_id", 1)])
        
        # Applications indexes
        apps_col = db["applications"]
        await apps_col.create_index([("profile_id", 1), ("updated_at", -1)])
        await apps_col.create_index([("status", 1)])
        
        # Events indexes (with TTL for auto-cleanup after 7 days)
        events_col = db["events"]
        await events_col.create_index([("user_id", 1), ("timestamp", -1)])
        await events_col.create_index([("timestamp", 1)], expireAfterSeconds=EVENTS_TTL_SECONDS)
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.warning(f"Error creating indexes (may already exist): {e}")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Jobly API - AI Job Hunter Agent",
        "version": "7.0.0",
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "readiness": "/readyz",
            "profile": "/profile",
            "cvs": "/cvs",
            "jobs": "/jobs",
            "matches": "/matches",
            "packets": "/packets",
            "interview": "/interview",
            "applications": "/applications",
            "prefill": "/prefill",
            "events": "/events/stream",
            "background_jobs": "/background-jobs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint - basic liveness check"""
    return {"status": "healthy"}


@app.get("/healthz")
async def healthz():
    """Kubernetes-style health check endpoint - basic liveness check"""
    return {"status": "healthy"}


@app.get("/readyz")
async def readyz():
    """
    Readiness check endpoint - checks if service is ready to accept traffic.
    
    Verifies:
    - Database connection is working
    """
    try:
        # Test database connection
        db = Database.get_database()
        # Perform a simple operation to verify connection
        await db.command("ping")
        
        return {
            "status": "ready",
            "database": "connected"
        }
    except Exception as e:
        from fastapi import Response
        return Response(
            content='{"status": "not ready", "error": "' + str(e) + '"}',
            status_code=503,
            media_type="application/json"
        )
