"""Interview preparation API endpoints"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime

from app.schemas.interview import (
    GenerateInterviewRequest,
    InterviewPackResponse,
    InterviewPackInDB,
    TechnicalQAInDB
)
from app.schemas.job_queue import JobType, JobResponse
from app.models.database import (
    get_packets_collection,
    get_profiles_collection,
    get_jobs_collection,
    get_interview_packs_collection,
    get_technical_qa_collection
)
from app.services.interview_prep import InterviewPrepService
from app.services.job_service import JobService
from app.services.sse_service import sse_service
from app.schemas.sse import SSEEvent, EventType
from app.schemas.packet import PacketInDB
from app.schemas.profile import UserProfile
from app.schemas.job import JobPostingInDB

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/generate", response_model=JobResponse)
async def generate_interview_materials(
    packet_id: str = Query(..., description="Packet ID to generate interview materials for")
):
    """
    Trigger background interview materials generation for a packet.
    
    Returns immediately with a job_id. Monitor progress via SSE /events/stream.
    """
    packets_col = get_packets_collection()
    
    # Validate packet exists
    packet_doc = await packets_col.find_one({"_id": packet_id})
    if not packet_doc:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Create background job
    job_service = JobService()
    job = await job_service.create_job(
        job_type=JobType.INTERVIEW_GENERATION,
        params={"packet_id": packet_id},
    )
    
    # Emit job created event
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_CREATED,
        data={
            "job_id": job.id,
            "type": job.type,
            "status": job.status,
            "message": "Interview generation queued"
        },
        user_id=job.user_id
    ))
    
    return JobResponse(
        job_id=job.id,
        type=job.type,
        status=job.status,
        message="Interview generation started. Monitor progress via /events/stream"
    )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate interview materials: {str(e)}"
        )


@router.get("/{packet_id}")
async def get_interview_materials(packet_id: str):
    """
    Retrieve interview materials for a packet
    
    Returns both interview pack and technical Q&A
    """
    interview_col = get_interview_packs_collection()
    qa_col = get_technical_qa_collection()
    
    # Get interview pack
    pack_doc = await interview_col.find_one({"_id": packet_id})
    if not pack_doc:
        raise HTTPException(
            status_code=404,
            detail="Interview materials not found. Generate them first with POST /interview/generate?packet_id=..."
        )
    
    # Get technical Q&A
    qa_doc = await qa_col.find_one({"_id": packet_id})
    if not qa_doc:
        raise HTTPException(
            status_code=404,
            detail="Technical Q&A not found"
        )
    
    return InterviewPackResponse(
        interview_pack=InterviewPackInDB(**pack_doc),
        technical_qa=TechnicalQAInDB(**qa_doc),
        message="Interview materials retrieved successfully"
    )
