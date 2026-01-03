"""Interview generation handler"""
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'api'))

from app.schemas.job_queue import BackgroundJobInDB
from app.services.job_service import JobService
from app.services.sse_service import SSEService
from app.schemas.sse import SSEEvent, EventType
from app.services.interview_prep import InterviewPrepService
from app.models.database import (
    get_packets_collection,
    get_profiles_collection,
    get_jobs_collection,
    get_interview_packs_collection,
    get_technical_qa_collection
)
from app.schemas.packet import PacketInDB
from app.schemas.profile import UserProfile
from app.schemas.job import JobPostingInDB

logger = logging.getLogger(__name__)


async def handle_interview_generation(
    job: BackgroundJobInDB,
    job_service: JobService,
    sse_service: SSEService
) -> dict:
    """
    Handle interview generation background job.
    
    Generates interview preparation materials for a packet.
    """
    logger.info(f"Starting interview generation for job {job.id}")
    
    packet_id = job.params.get("packet_id")
    if not packet_id:
        raise ValueError("packet_id is required in job params")
    
    # Update progress
    await job_service.update_progress(job.id, 10, "Loading packet data...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 10,
            "message": "Loading packet data..."
        },
        user_id=job.user_id
    ))
    
    # Get packet, profile, and job
    packets_col = get_packets_collection()
    profiles_col = get_profiles_collection()
    jobs_col = get_jobs_collection()
    interview_col = get_interview_packs_collection()
    qa_col = get_technical_qa_collection()
    
    packet_doc = await packets_col.find_one({"_id": packet_id})
    if not packet_doc:
        raise ValueError(f"Packet {packet_id} not found")
    
    packet = PacketInDB(**packet_doc)
    
    profile_doc = await profiles_col.find_one({})
    if not profile_doc:
        raise ValueError("Profile not found")
    
    profile = UserProfile(**profile_doc)
    
    job_doc = await jobs_col.find_one({"_id": packet.job_id})
    if not job_doc:
        raise ValueError(f"Job {packet.job_id} not found")
    
    job_posting = JobPostingInDB(**job_doc)
    
    # Update progress
    await job_service.update_progress(job.id, 30, "Generating interview pack...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 30,
            "message": "Generating interview pack..."
        },
        user_id=job.user_id
    ))
    
    # Generate interview materials
    service = InterviewPrepService()
    
    interview_pack = await service.generate_interview_pack(profile, job_posting, packet)
    
    # Update progress
    await job_service.update_progress(job.id, 60, "Generating technical Q&A...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 60,
            "message": "Generating technical Q&A..."
        },
        user_id=job.user_id
    ))
    
    technical_qa = await service.generate_technical_qa(profile, job_posting, packet)
    
    # Update progress
    await job_service.update_progress(job.id, 85, "Saving to database...")
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_PROGRESS,
        data={
            "job_id": job.id,
            "type": job.type,
            "progress": 85,
            "message": "Saving to database..."
        },
        user_id=job.user_id
    ))
    
    # Store in database
    interview_pack_dict = interview_pack.model_dump()
    interview_pack_dict["_id"] = packet_id
    
    technical_qa_dict = technical_qa.model_dump()
    technical_qa_dict["_id"] = packet_id
    
    # Upsert
    await interview_col.replace_one(
        {"_id": packet_id},
        interview_pack_dict,
        upsert=True
    )
    
    await qa_col.replace_one(
        {"_id": packet_id},
        technical_qa_dict,
        upsert=True
    )
    
    logger.info(f"Interview generation completed for packet {packet_id}")
    
    return {
        "result": {"packet_id": packet_id},
        "resource_refs": {"packet_id": packet_id},
        "message": f"Interview materials generated for packet {packet_id}"
    }
