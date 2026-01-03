"""Match recompute handler"""
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from app.schemas.job_queue import BackgroundJobInDB
from app.services.job_service import JobService
from app.services.sse_service import SSEService
from app.services.matching.match_service import MatchGenerationService
from app.schemas.sse import SSEEvent, EventType

logger = logging.getLogger(__name__)


async def handle_match_recompute(
    job: BackgroundJobInDB,
    job_service: JobService,
    sse_service: SSEService
) -> dict:
    """
    Handle match recompute background job.
    
    Recomputes all matches for the given profile against all jobs.
    """
    logger.info(f"Starting match recompute for job {job.id}")
    
    profile_id = job.params.get("profile_id")
    if not profile_id:
        raise ValueError("profile_id is required in job params")
    
    # Update progress
    await job_service.update_progress(job.id, 10, "Initializing match computation...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 10,
            "message": "Initializing match computation..."
        },
        user_id=job.user_id
    ))
    
    # Recompute matches
    service = MatchGenerationService()
    
    # Update progress
    await job_service.update_progress(job.id, 30, "Computing matches...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 30,
            "message": "Computing matches..."
        },
        user_id=job.user_id
    ))
    
    matches_computed = await service.recompute_all_matches(profile_id)
    
    # Update progress
    await job_service.update_progress(job.id, 90, "Finalizing...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 90,
            "message": "Finalizing..."
        },
        user_id=job.user_id
    ))
    
    logger.info(f"Match recompute completed: {matches_computed} matches")
    
    return {
        "result": {"matches_computed": matches_computed},
        "message": f"Successfully computed {matches_computed} matches"
    }
