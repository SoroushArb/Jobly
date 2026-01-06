"""
Background jobs API endpoints
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.schemas.job_queue import (
    JobCreateRequest,
    JobResponse,
    JobListResponse,
    BackgroundJobInDB,
    JobType,
    JobStatus,
)
from app.services.job_service import JobService


router = APIRouter(prefix="/background-jobs", tags=["background-jobs"])
job_service = JobService()


@router.post("", response_model=JobResponse)
async def create_job(request: JobCreateRequest):
    """
    Create a new background job.
    
    This is typically used internally by other endpoints,
    but can also be used directly for testing.
    """
    job = await job_service.create_job(
        job_type=request.type,
        params=request.params,
        user_id=request.user_id,
    )
    
    return JobResponse(
        job_id=job.id,
        type=job.type,
        status=job.status,
        message=f"Job {job.id} created successfully",
    )


@router.get("", response_model=JobListResponse)
async def list_jobs(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    status: Optional[JobStatus] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
):
    """
    List background jobs with optional filters.
    """
    skip = (page - 1) * per_page
    jobs, total = await job_service.list_jobs(
        user_id=user_id,
        job_type=job_type,
        status=status,
        skip=skip,
        limit=per_page,
    )
    
    return JobListResponse(
        jobs=jobs,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{job_id}", response_model=BackgroundJobInDB)
async def get_job(job_id: str):
    """
    Get a specific job by ID.
    """
    job = await job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job
