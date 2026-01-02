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
from app.models.database import (
    get_packets_collection,
    get_profiles_collection,
    get_jobs_collection,
    get_interview_packs_collection,
    get_technical_qa_collection
)
from app.services.interview_prep import InterviewPrepService
from app.schemas.packet import PacketInDB
from app.schemas.profile import UserProfile
from app.schemas.job import JobPostingInDB

router = APIRouter(prefix="/interview", tags=["interview"])


@router.post("/generate")
async def generate_interview_materials(
    packet_id: str = Query(..., description="Packet ID to generate interview materials for")
):
    """
    Generate interview preparation materials for a packet
    
    Creates:
    - Interview pack with STAR stories, 30/60/90 plan, questions
    - Technical Q&A with gap-aware question prioritization
    """
    packets_col = get_packets_collection()
    profiles_col = get_profiles_collection()
    jobs_col = get_jobs_collection()
    interview_col = get_interview_packs_collection()
    qa_col = get_technical_qa_collection()
    
    # Get packet
    packet_doc = await packets_col.find_one({"_id": packet_id})
    if not packet_doc:
        raise HTTPException(status_code=404, detail="Packet not found")
    
    packet = PacketInDB(**packet_doc)
    
    # Get profile
    profile_doc = await profiles_col.find_one({})  # Single profile system
    if not profile_doc:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    profile = UserProfile(**profile_doc)
    
    # Get job
    job_doc = await jobs_col.find_one({"_id": packet.job_id})
    if not job_doc:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = JobPostingInDB(**job_doc)
    
    # Generate interview materials
    service = InterviewPrepService()
    
    try:
        interview_pack = await service.generate_interview_pack(profile, job, packet)
        technical_qa = await service.generate_technical_qa(profile, job, packet)
        
        # Store in database
        interview_pack_dict = interview_pack.model_dump()
        interview_pack_dict["_id"] = packet_id  # Use packet_id as key
        
        technical_qa_dict = technical_qa.model_dump()
        technical_qa_dict["_id"] = packet_id  # Use packet_id as key
        
        # Upsert (replace if exists)
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
        
        # Retrieve saved documents
        saved_pack = await interview_col.find_one({"_id": packet_id})
        saved_qa = await qa_col.find_one({"_id": packet_id})
        
        return InterviewPackResponse(
            interview_pack=InterviewPackInDB(**saved_pack),
            technical_qa=TechnicalQAInDB(**saved_qa),
            message="Interview materials generated successfully"
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
