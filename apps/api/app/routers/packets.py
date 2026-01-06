"""Packets router for CV generation and application materials"""
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from typing import Optional
from pathlib import Path

from app.schemas.packet import (
    GeneratePacketRequest,
    PacketResponse,
    PacketListResponse,
    Packet,
    PacketInDB,
    TailoringPlan,
)
from app.schemas.job_queue import JobType, JobResponse
from app.schemas.profile import UserProfile
from app.schemas.job import JobPosting
from app.models.database import get_profiles_collection, get_jobs_collection
from app.services.tailoring import TailoringService
from app.services.packet_storage import PacketStorageService
from app.services.job_service import JobService
from app.services.sse_service import sse_service
from app.schemas.sse import SSEEvent, EventType
from bson import ObjectId


router = APIRouter(prefix="/packets", tags=["packets"])

tailoring_service = TailoringService()
storage_service = PacketStorageService()


async def get_user_profile() -> UserProfile:
    """Get the user's profile (simplified - assumes single user)"""
    collection = get_profiles_collection()
    profile_data = await collection.find_one({})
    
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found. Please create a profile first.")
    
    profile_data["_id"] = str(profile_data["_id"])
    return UserProfile(**profile_data)


async def get_job_by_id(job_id: str) -> JobPosting:
    """Get job posting by ID"""
    collection = get_jobs_collection()
    
    try:
        job_data = await collection.find_one({"_id": ObjectId(job_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid job ID format")
    
    if not job_data:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_data["_id"] = str(job_data["_id"])
    return JobPosting(**job_data)


@router.post("/generate", response_model=JobResponse)
async def generate_packet(request: GeneratePacketRequest):
    """
    Trigger background packet generation for a job.
    
    Returns immediately with a job_id. Monitor progress via SSE /events/stream.
    """
    # Validate job exists
    await get_job_by_id(request.job_id)
    
    # Create background job
    job_service = JobService()
    job = await job_service.create_job(
        job_type=JobType.PACKET_GENERATION,
        params={
            "job_id": request.job_id,
            "user_emphasis": request.user_emphasis,
        },
    )
    
    # Emit job created event
    await sse_service.emit(SSEEvent(
        event_type=EventType.JOB_CREATED,
        data={
            "job_id": job.id,
            "type": job.type,
            "status": job.status,
            "message": "Packet generation queued"
        },
        user_id=job.user_id
    ))
    
    return JobResponse(
        job_id=job.id,
        type=job.type,
        status=job.status,
        message="Packet generation started. Monitor progress via /events/stream"
    )


@router.get("/{packet_id}", response_model=PacketResponse)
async def get_packet(packet_id: str):
    """Get packet details by ID"""
    packet = await storage_service.get_packet(packet_id)
    
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    return PacketResponse(packet=packet)


@router.get("", response_model=PacketListResponse)
async def list_packets(
    profile_id: Optional[str] = Query(None, description="Filter by profile ID"),
    job_id: Optional[str] = Query(None, description="Filter by job ID"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100)
):
    """List all packets with optional filtering"""
    skip = (page - 1) * per_page
    
    packets, total = await storage_service.list_packets(
        profile_id=profile_id,
        job_id=job_id,
        skip=skip,
        limit=per_page
    )
    
    return PacketListResponse(
        packets=packets,
        total=total,
        page=page,
        per_page=per_page
    )


@router.get("/{packet_id}/download/{file_type}")
async def download_file(packet_id: str, file_type: str):
    """
    Download a file from the packet.
    
    file_type: tex, pdf, cover_letter, recruiter_message, common_answers
    """
    packet = await storage_service.get_packet(packet_id)
    
    if not packet:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    # Map file type to packet file
    file_map = {
        "tex": packet.cv_tex,
        "pdf": packet.cv_pdf,
        "cover_letter": packet.cover_letter,
        "recruiter_message": packet.recruiter_message,
        "common_answers": packet.common_answers,
    }
    
    packet_file = file_map.get(file_type)
    
    if not packet_file:
        raise HTTPException(status_code=404, detail=f"File type '{file_type}' not available for this packet")
    
    file_path = storage_service.get_file_path(packet_file)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
    
    return FileResponse(
        path=file_path,
        filename=packet_file.filename,
        media_type="application/octet-stream"
    )
