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
    IngestResponse
)
from app.models.database import Database
from app.services.job_ingestion import JobIngestionService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest_jobs():
    """
    Manual trigger for job ingestion from all configured sources
    
    This endpoint fetches jobs from all enabled sources in job_sources_config.yaml,
    parses them, and stores them in MongoDB with deduplication.
    """
    try:
        service = JobIngestionService()
        result = await service.ingest_all()
        
        return IngestResponse(
            jobs_fetched=result["jobs_fetched"],
            jobs_new=result["jobs_new"],
            jobs_updated=result["jobs_updated"],
            sources_processed=result["sources_processed"],
            message=f"Ingestion completed: {result['jobs_new']} new, {result['jobs_updated']} updated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("", response_model=JobListResponse)
async def list_jobs(
    remote_type: Optional[str] = Query(None, description="Filter by remote type: onsite/hybrid/remote/unknown"),
    remote: Optional[bool] = Query(None, description="Filter for remote jobs only (shorthand)"),
    country: Optional[str] = Query(None, description="Filter by country"),
    city: Optional[str] = Query(None, description="Filter by city"),
    keyword: Optional[str] = Query(None, description="Search in title, company, or description"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=100, description="Results per page")
):
    """
    List job postings with optional filters
    
    Supports filtering by:
    - remote_type: onsite/hybrid/remote/unknown
    - remote: boolean shorthand for remote jobs
    - country: exact country match
    - city: exact city match
    - keyword: search in title, company, or description
    
    Pagination:
    - page: page number (default 1)
    - per_page: results per page (default 50, max 100)
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
        
        if keyword:
            # Search in multiple fields
            query["$or"] = [
                {"title": {"$regex": keyword, "$options": "i"}},
                {"company": {"$regex": keyword, "$options": "i"}},
                {"description_clean": {"$regex": keyword, "$options": "i"}}
            ]
        
        # Count total matching documents
        total = await jobs_collection.count_documents(query)
        
        # Get paginated results
        skip = (page - 1) * per_page
        cursor = jobs_collection.find(query).sort("fetched_at", -1).skip(skip).limit(per_page)
        
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
