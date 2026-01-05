"""Job ingestion handler"""
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from app.schemas.job_queue import BackgroundJobInDB
from app.services.job_service import JobService
from app.services.sse_service import SSEService
from app.services.job_ingestion import JobIngestionService
from app.schemas.sse import SSEEvent, EventType

logger = logging.getLogger(__name__)


async def handle_job_ingestion(
    job: BackgroundJobInDB,
    job_service: JobService,
    sse_service: SSEService
) -> dict:
    """
    Handle job ingestion background job.
    
    Fetches jobs from all configured sources and stores them in the database.
    """
    logger.info(f"Starting job ingestion for job {job.id}")
    
    # Update progress
    await job_service.update_progress(job.id, 10, "Initializing job ingestion...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 10,
            "message": "Initializing job ingestion..."
        },
        user_id=job.user_id
    ))
    
    # Run ingestion
    service = JobIngestionService()
    
    # Update progress
    await job_service.update_progress(job.id, 30, "Fetching jobs from sources...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 30,
            "message": "Fetching jobs from sources..."
        },
        user_id=job.user_id
    ))
    
    result = await service.ingest_all()
    
    # Update progress
    await job_service.update_progress(job.id, 90, "Saving jobs to database...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 90,
            "message": "Saving jobs to database..."
        },
        user_id=job.user_id
    ))
    
    logger.info(f"Job ingestion completed: {result['jobs_new']} new, {result['jobs_updated']} updated")
    
    return {
        "result": result,
        "message": f"Ingestion completed: {result['jobs_new']} new, {result['jobs_updated']} updated"
    }
