from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import profile_router, jobs_router
from app.models import Database
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Jobly API",
    description="AI Job Hunter Agent - User Profile Management & Job Ingestion",
    version="2.0.0"
)

# Configure CORS
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(profile_router)
app.include_router(jobs_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    Database.get_client()
    print("Database connection initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await Database.close()
    print("Database connection closed")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Jobly API - AI Job Hunter Agent",
        "version": "2.0.0",
        "endpoints": {
            "docs": "/docs",
            "profile": "/profile",
            "jobs": "/jobs"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
