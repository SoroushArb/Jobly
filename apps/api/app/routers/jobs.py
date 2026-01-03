"""
Job management API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas import (
    JobPostingInDB,
    JobPostingResponse,
    JobListResponse,
    IngestResponse,
    JobType,
    JobResponse,
)
from app.models.database import Database
from app.services.job_ingestion import JobIngestionService
from app.services.job_service import JobService
from app.services.sse_service import sse_service
from app.schemas.sse import SSEEvent, EventType

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/ingest", response_model=JobResponse)
async def ingest_jobs():
    """
    Trigger background job ingestion from all configured sources.
    
    Returns immediately with a job_id. Monitor progress via SSE /events/stream.
    """
    try:
        job_service = JobService()
        
        # Create background job
        job = await job_service.create_job(
            job_type=JobType.JOB_INGESTION,
            params={},
        )
        
        # Emit job created event
        await sse_service.emit(SSEEvent(
            event_type=EventType.JOB_CREATED,
            data={
                "job_id": job.id,
                "type": job.type,
                "status": job.status,
                "message": "Job ingestion queued"
            },
            user_id=job.user_id
        ))
        
        return JobResponse(
            job_id=job.id,
            type=job.type,
            status=job.status,
            message="Job ingestion started. Monitor progress via /events/stream"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion: {str(e)}")


@router.get("", response_model=JobListResponse)
async def list_jobs(
    remote_type: Optional[str] = Query(None, description="Filter by remote type: onsite/hybrid/remote/unknown"),
    remote: Optional[bool] = Query(None, description="Filter for remote jobs only (shorthand)"),
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    keyword: Optional[str] = Query(None, description="Search in title, company, or description"),
    title: Optional[str] = Query(None, description="Search specifically in job title (higher relevance)"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page")
):
    """
    List job postings with optional filters
    
    Supports filtering by:
    - remote_type: onsite/hybrid/remote/unknown
    - remote: boolean shorthand for remote jobs
    - country: exact or partial country match
    - city: exact or partial city match
    - keyword: search in title, company, or description
    - title: search specifically in job title (more relevant than keyword)
    
    Pagination:
    - page: page number (default 1)
    - per_page: results per page (default 50, max 100)
    
    When 'title' filter is used, results are sorted by relevance (title match score)
    """
    try:
        db = Database.get_database()
        jobs_collection = db["jobs"]
        
        # Build query filter
        query = {}
        
        if remote_type:
            query["remote_type"] = remote_type
        elif remote:
            query["remote_type"] = "remote"
        
        if country:
            query["country"] = {"$regex": country, "$options": "i"}
        
        if city:
            query["city"] = {"$regex": city, "$options": "i"}
        
        # Handle title-specific search vs general keyword search
        if title:
            # Title-specific search with higher priority
            query["title"] = {"$regex": title, "$options": "i"}
        elif keyword:
            # General search across multiple fields
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"company": {"$regex": keyword, "$options": "i"}},
                {"description_clean": {"$regex": keyword, "$options": "i"}}
            ]
        
        # Count total matching documents
        total = await jobs_collection.count_documents(query)
        
        # Determine sorting strategy
        if title:
            # For title searches, sort by fetched_at (most recent first)
            # MongoDB's text search score would be better but requires text index
            sort_field = "fetched_at"
            sort_direction = -1
        else:
            # Default: most recently fetched jobs first
            sort_field = "fetched_at"
            sort_direction = -1
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = jobs_collection.find(query).sort(sort_field, sort_direction).skip(skip).limit(per_page)
        
        jobs = []
        async for job_doc in cursor:
            # Convert MongoDB _id to string
            if "_id" in job_doc:
                job_doc["_id"] = str(job_doc["_id"])
            jobs.append(JobPostingInDB(**job_doc))
        
        return JobListResponse(
            jobs=jobs,
            total=total,
            page=page,
            per_page=per_page,
            message=f"Found {total} jobs"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobPostingResponse)
async def get_job(job_id: str):
    """
    Get a single job posting by ID
    
    Args:
        job_id: MongoDB ObjectId as string
    """
    try:
        from bson import ObjectId
        
        db = Database.get_database()
        jobs_collection = db["jobs"]
        
        # Find job by ID
        job_doc = await jobs_collection.find_one({"_id": ObjectId(job_id)})
        
        if not job_doc:
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Convert MongoDB _id to string
        job_doc["_id"] = str(job_doc["_id"])
        
        return JobPostingResponse(
            job=JobPostingInDB(**job_doc),
            message="Job retrieved successfully"
        )
        
    except Exception as e:
        if "not found" in str(e).lower():
            raise
        raise HTTPException(status_code=500, detail=f"Failed to fetch job: {str(e)}")


@router.get("/sources/info")
async def get_sources_info():
    """
    Get information about configured job sources
    
    Returns list of sources with their configuration and compliance notes
    """
    try:
        service = JobIngestionService()
        sources = service.get_sources_info()
        
        return {
            "sources": sources,
            "total": len(sources),
            "message": "Sources info retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get sources info: {str(e)}")


@router.post("/manual-import")
async def manual_job_import(
    url: str,
    title: str,
    company: str,
    location: Optional[str] = None,
    remote_type: Optional[str] = "unknown",
    description: Optional[str] = None
):
    """
    Manually import a job from a URL (e.g., LinkedIn, Indeed)
    
    This endpoint allows users to add jobs from sources that cannot be
    legally scraped. The user provides the URL and basic job details.
    
    Args:
        url: Job posting URL
        title: Job title
        company: Company name
        location: Job location (optional, format: "City, Country" or "City")
        remote_type: Remote type (onsite/hybrid/remote/unknown)
        description: Job description (optional)
        
    Returns:
        Success message with job ID
    """
    try:
        from datetime import datetime
        import hashlib
        
        db = Database.get_database()
        jobs_collection = db["jobs"]
        
        # Parse location into city/country if provided
        city = None
        country = None
        if location and location.strip():
            # Expected format: "City, Country" or just "City"
            parts = [p.strip() for p in location.split(',') if p.strip()]
            if len(parts) >= 2:
                city = parts[0]
                country = parts[-1]
            elif len(parts) == 1:
                city = parts[0]
        
        # Create job posting
        job_data = {
            "title": title,
            "company": company,
            "location": location or "Not specified",
            "city": city,
            "country": country,
            "remote_type": remote_type,
            "url": url,
            "description_clean": description or f"Manually imported job: {title} at {company}",
            "employment_type": None,
            "source_name": "Manual Import",
            "source_compliance_note": "User-provided URL - no scraping performed",
            "first_seen": datetime.utcnow(),
            "last_seen": datetime.utcnow(),
            "fetched_at": datetime.utcnow(),
        }
        
        # Create dedupe hash based on URL
        dedupe_string = f"{url.lower()}"
        job_data["dedupe_hash"] = hashlib.sha256(dedupe_string.encode()).hexdigest()
        
        # Check if job already exists
        existing = await jobs_collection.find_one({"dedupe_hash": job_data["dedupe_hash"]})
        
        if existing:
            # Update last_seen
            await jobs_collection.update_one(
                {"dedupe_hash": job_data["dedupe_hash"]},
                {"$set": {"last_seen": datetime.utcnow()}}
            )
            return {
                "message": "Job already exists (updated last_seen)",
                "job_id": str(existing["_id"]),
                "is_new": False
            }
        else:
            # Insert new job
            result = await jobs_collection.insert_one(job_data)
            return {
                "message": "Job imported successfully",
                "job_id": str(result.inserted_id),
                "is_new": True
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import job: {str(e)}")
