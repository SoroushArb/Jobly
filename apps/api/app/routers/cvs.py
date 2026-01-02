"""
CV Document management endpoints - multi-CV support
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from bson import ObjectId

from app.schemas import (
    CVDocumentInDB,
    CVListResponse,
    CVDocumentResponse,
    SetActiveCVRequest,
)
from app.models.database import get_cv_documents_collection

router = APIRouter(prefix="/cvs", tags=["cv-documents"])


@router.get("", response_model=CVListResponse)
async def list_cvs(user_email: str = Query(..., description="User email")):
    """
    List all CV documents for a user
    
    Args:
        user_email: Email address of the user
        
    Returns:
        List of CV documents sorted by upload date (most recent first)
    """
    try:
        collection = get_cv_documents_collection()
        
        # Find all CVs for this user
        cursor = collection.find({"user_email": user_email}).sort("upload_date", -1)
        
        cvs = []
        async for cv_doc in cursor:
            # Convert MongoDB _id to string
            cv_doc["_id"] = str(cv_doc["_id"])
            cvs.append(CVDocumentInDB(**cv_doc))
        
        return CVListResponse(
            cvs=cvs,
            total=len(cvs),
            message=f"Found {len(cvs)} CVs for {user_email}"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving CVs: {str(e)}")


@router.post("/set-active", response_model=CVDocumentResponse)
async def set_active_cv(request: SetActiveCVRequest):
    """
    Set a CV document as the active one for a user
    
    Args:
        request: Contains cv_id and user_email
        
    Returns:
        Success message with CV ID
    """
    try:
        collection = get_cv_documents_collection()
        
        # First, deactivate all CVs for this user
        await collection.update_many(
            {"user_email": request.user_email},
            {"$set": {"is_active": False}}
        )
        
        # Then, activate the specified CV
        result = await collection.update_one(
            {"_id": ObjectId(request.cv_id), "user_email": request.user_email},
            {"$set": {"is_active": True}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=404,
                detail=f"CV {request.cv_id} not found for user {request.user_email}"
            )
        
        return CVDocumentResponse(
            cv_id=request.cv_id,
            message="CV set as active successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting active CV: {str(e)}")


@router.delete("/{cv_id}")
async def delete_cv(cv_id: str, user_email: str = Query(..., description="User email")):
    """
    Delete a CV document
    
    Args:
        cv_id: MongoDB ObjectId of the CV document
        user_email: Email address of the user (for security)
        
    Returns:
        Success message
    """
    try:
        collection = get_cv_documents_collection()
        
        # Check if this is the active CV
        cv_doc = await collection.find_one({"_id": ObjectId(cv_id), "user_email": user_email})
        
        if not cv_doc:
            raise HTTPException(
                status_code=404,
                detail=f"CV {cv_id} not found for user {user_email}"
            )
        
        was_active = cv_doc.get("is_active", False)
        
        # Delete the CV
        result = await collection.delete_one({"_id": ObjectId(cv_id), "user_email": user_email})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="CV not found")
        
        # If deleted CV was active, set the most recent one as active
        if was_active:
            cursor = collection.find({"user_email": user_email}).sort("upload_date", -1).limit(1)
            most_recent = await cursor.to_list(length=1)
            
            if most_recent:
                await collection.update_one(
                    {"_id": most_recent[0]["_id"]},
                    {"$set": {"is_active": True}}
                )
        
        return {"message": "CV deleted successfully", "cv_id": cv_id}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting CV: {str(e)}")


@router.get("/active")
async def get_active_cv(user_email: str = Query(..., description="User email")):
    """
    Get the currently active CV for a user
    
    Args:
        user_email: Email address of the user
        
    Returns:
        Active CV document
    """
    try:
        collection = get_cv_documents_collection()
        
        # Find the active CV
        cv_doc = await collection.find_one({"user_email": user_email, "is_active": True})
        
        if not cv_doc:
            # If no active CV, get the most recent one
            cursor = collection.find({"user_email": user_email}).sort("upload_date", -1).limit(1)
            most_recent = await cursor.to_list(length=1)
            
            if not most_recent:
                raise HTTPException(
                    status_code=404,
                    detail=f"No CVs found for user {user_email}"
                )
            
            cv_doc = most_recent[0]
            # Set it as active
            await collection.update_one(
                {"_id": cv_doc["_id"]},
                {"$set": {"is_active": True}}
            )
        
        # Convert MongoDB _id to string
        cv_doc["_id"] = str(cv_doc["_id"])
        
        return CVDocumentInDB(**cv_doc)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving active CV: {str(e)}")
