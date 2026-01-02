from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from app.schemas import (
    UserProfile,
    UserProfileUpdate,
    UploadCVResponse,
    ProfileResponse,
    ProfileSaveResponse,
    CVDocument,
    CVDocumentResponse,
)
from app.services import CVExtractor
from app.models import get_profiles_collection
from app.models.database import get_cv_documents_collection
from datetime import datetime
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/profile", tags=["profile"])


def _should_update_field(key: str, value: any, is_update: bool) -> bool:
    """
    Determine if a field should be updated in the profile.
    
    Args:
        key: Field name
        value: Field value
        is_update: True if updating existing profile, False if creating new
        
    Returns:
        True if field should be updated, False otherwise
    """
    # Always update metadata fields
    if key in ["updated_at", "schema_version"]:
        return True
    
    # For new profiles, include all non-None values
    if not is_update:
        return value is not None
    
    # For updates, only update if value is truthy or explicitly provided
    if value is None:
        return False
    
    # For lists/dicts, only update if not empty (prevents accidental clearing)
    if isinstance(value, (list, dict)):
        return len(value) > 0
    
    # For other types, update if value exists
    return True


@router.post("/upload-cv", response_model=UploadCVResponse)
async def upload_cv(file: UploadFile = File(...)):
    """
    Upload a CV file (PDF or DOCX) and extract profile information
    
    This endpoint now supports multi-CV:
    - Stores the CV document in cv_documents collection
    - Creates/updates profile from CV data
    - Returns draft_profile for immediate use
    
    Returns:
        - extracted_text: Raw text extracted from the CV
        - draft_profile: Schema-valid UserProfile with extracted data
        - cv_id: ID of the stored CV document
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
        
        # Store CV document in cv_documents collection
        cv_collection = get_cv_documents_collection()
        
        # Deactivate all previous CVs for this user
        await cv_collection.update_many(
            {"user_email": draft_profile.email},
            {"$set": {"is_active": False}}
        )
        
        # Create new CV document
        cv_document = CVDocument(
            user_email=draft_profile.email,
            filename=file.filename,
            extracted_text=extracted_text,
            parsed_profile=draft_profile.model_dump(),
            is_active=True,  # New uploads are active by default
            upload_date=datetime.utcnow()
        )
        
        result = await cv_collection.insert_one(cv_document.model_dump())
        cv_id = str(result.inserted_id)
        
        # Also save/update the profile in profiles collection (for backward compatibility)
        profiles_collection = get_profiles_collection()
        profile_dict = draft_profile.model_dump()
        profile_dict["updated_at"] = datetime.utcnow()
        
        existing = await profiles_collection.find_one({"email": draft_profile.email})
        if existing:
            await profiles_collection.update_one(
                {"email": draft_profile.email},
                {"$set": profile_dict}
            )
        else:
            await profiles_collection.insert_one(profile_dict)
        
        return UploadCVResponse(
            extracted_text=extracted_text,
            draft_profile=draft_profile,
            message=f"CV processed successfully. CV ID: {cv_id}"
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
        message: Success message with details
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
            # For updates, only update fields that should be updated
            # to prevent accidental data loss
            update_dict = {}
            for key, value in profile_dict.items():
                if _should_update_field(key, value, is_update=True):
                    update_dict[key] = value
            
            # Update existing profile
            result = await collection.update_one(
                {"email": profile.email},
                {"$set": update_dict}
            )
            profile_id = str(existing["_id"])
            action = "updated"
        else:
            # For new profiles, include all provided fields
            insert_dict = {
                k: v for k, v in profile_dict.items()
                if _should_update_field(k, v, is_update=False)
            }
            
            # Insert new profile
            result = await collection.insert_one(insert_dict)
            profile_id = str(result.inserted_id)
            action = "created"
        
        return ProfileSaveResponse(
            profile_id=profile_id,
            message=f"Profile {action} successfully for {profile.email}"
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


@router.post("/preferences/save", response_model=ProfileSaveResponse)
async def save_preferences(email: str, preferences: dict):
    """
    Save job search preferences for a user profile
    
    Args:
        email: Email address of profile
        preferences: Preferences object as dict
        
    Returns:
        Success message with profile ID
    """
    try:
        collection = get_profiles_collection()
        
        # Get existing profile
        existing = await collection.find_one({"email": email})
        if not existing:
            raise HTTPException(
                status_code=404,
                detail=f"Profile not found for email: {email}"
            )
        
        # Update preferences
        result = await collection.update_one(
            {"email": email},
            {
                "$set": {
                    "preferences": preferences,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.modified_count == 0:
            # Check if preferences are the same
            if existing.get("preferences") == preferences:
                return ProfileSaveResponse(
                    profile_id=str(existing["_id"]),
                    message="Preferences unchanged (already up to date)"
                )
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to update preferences"
                )
        
        return ProfileSaveResponse(
            profile_id=str(existing["_id"]),
            message="Preferences saved successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving preferences: {str(e)}")
