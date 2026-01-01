from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import (
    UserProfile,
    UserProfileUpdate,
    UploadCVResponse,
    ProfileResponse,
    ProfileSaveResponse,
)
from app.services import CVExtractor
from app.models import get_profiles_collection
from datetime import datetime
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/upload-cv", response_model=UploadCVResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV file (PDF or DOCX) and extract profile information
    
    Returns:
        - extracted_text: Raw text extracted from the CV
        - draft_profile: Schema-valid UserProfile with extracted data
    """
    try:
        # Read file content
        content = await file.read()
        
        # Determine file type and extract text
        if file.filename.lower().endswith('.pdf'):
            extracted_text, evidence_map = CVExtractor.extract_text_from_pdf(content)
        elif file.filename.lower().endswith(('.docx', '.doc')):
            extracted_text, evidence_map = CVExtractor.extract_text_from_docx(content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload PDF or DOCX files."
            )
        
        # Create draft profile from extracted text
        draft_profile = CVExtractor.create_draft_profile(extracted_text, evidence_map)
        
        return UploadCVResponse(
            extracted_text=extracted_text,
            draft_profile=draft_profile,
            message="CV processed successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CV: {str(e)}")


@router.post("/save", response_model=ProfileSaveResponse)
async def save_profile(profile: UserProfile):
    """
    Save a user profile to MongoDB
    
    Args:
        profile: Complete UserProfile object
        
    Returns:
        profile_id: MongoDB ObjectId of saved profile
    """
    try:
        collection = get_profiles_collection()
        
        # Update timestamp
        profile.updated_at = datetime.utcnow()
        
        # Convert to dict for MongoDB
        profile_dict = profile.model_dump()
        
        # Check if profile exists (by email)
        existing = await collection.find_one({"email": profile.email})
        
        if existing:
            # Update existing profile
            result = await collection.update_one(
                {"email": profile.email},
                {"$set": profile_dict}
            )
            profile_id = str(existing["_id"])
        else:
            # Insert new profile
            result = await collection.insert_one(profile_dict)
            profile_id = str(result.inserted_id)
        
        return ProfileSaveResponse(
            profile_id=profile_id,
            message="Profile saved successfully"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving profile: {str(e)}")


@router.get("", response_model=ProfileResponse)
async def get_profile(email: Optional[str] = None):
    """
    Retrieve a user profile from MongoDB
    
    Args:
        email: Email address to retrieve profile for (defaults to most recent)
        
    Returns:
        UserProfile object
    """
    try:
        collection = get_profiles_collection()
        
        if email:
            profile_dict = await collection.find_one({"email": email})
        else:
            # Get most recently updated profile
            cursor = collection.find().sort("updated_at", -1).limit(1)
            profiles = await cursor.to_list(length=1)
            profile_dict = profiles[0] if profiles else None
        
        if not profile_dict:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Remove MongoDB _id field
        profile_dict.pop("_id", None)
        
        # Parse into UserProfile
        profile = UserProfile(**profile_dict)
        
        return ProfileResponse(
            profile=profile,
            message="Profile retrieved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving profile: {str(e)}")


@router.patch("", response_model=ProfileSaveResponse)
async def update_profile(email: str, updates: UserProfileUpdate):
    """
    Update specific fields of a user profile
    
    Args:
        email: Email address of profile to update
        updates: Fields to update (only provided fields will be updated)
        
    Returns:
        profile_id: MongoDB ObjectId of updated profile
    """
    try:
        collection = get_profiles_collection()
        
        # Get existing profile
        existing = await collection.find_one({"email": email})
        if not existing:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # Build update dict (only non-None fields)
        update_dict = {
            k: v for k, v in updates.model_dump(exclude_unset=True).items() 
            if v is not None
        }
        
        # Add updated timestamp
        update_dict["updated_at"] = datetime.utcnow()
        
        # Update profile
        await collection.update_one(
            {"email": email},
            {"$set": update_dict}
        )
        
        return ProfileSaveResponse(
            profile_id=str(existing["_id"]),
            message="Profile updated successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {str(e)}")
