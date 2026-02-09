from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from datetime import datetime, timedelta
import secrets
from typing import Optional

from app.schemas.analysis import AnalysisDetail
from app.core.security import get_current_user
from app.core.database import get_database

router = APIRouter()


@router.post("/{analysis_id}/share")
async def create_share_link(
    analysis_id: str,
    expires_in_days: int = 7,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Create a shareable link for analysis"""
    db = get_database()
    
    try:
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis ID"
        )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Check if user owns this analysis
    if current_user and analysis.get('user_id') != current_user.get('user_id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to share this analysis"
        )
    
    # Generate unique share token
    share_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # Create share record
    share_data = {
        "analysis_id": analysis_id,
        "share_token": share_token,
        "created_by": current_user.get('user_id') if current_user else None,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "view_count": 0,
        "is_active": True
    }
    
    await db.shares.insert_one(share_data)
    
    # Update analysis with share info
    await db.analyses.update_one(
        {"_id": ObjectId(analysis_id)},
        {"$set": {"is_shared": True, "last_shared_at": datetime.utcnow()}}
    )
    
    share_url = f"/share/{share_token}"
    
    return {
        "share_token": share_token,
        "share_url": share_url,
        "expires_at": expires_at,
        "message": "Share link created successfully"
    }


@router.get("/{share_token}")
async def get_shared_analysis(share_token: str):
    """Get analysis via share link"""
    db = get_database()
    
    # Find share record
    share = await db.shares.find_one({"share_token": share_token})
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    # Check if expired
    if share.get('expires_at') < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Share link has expired"
        )
    
    # Check if active
    if not share.get('is_active', True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Share link has been deactivated"
        )
    
    # Get analysis
    analysis_id = share.get('analysis_id')
    try:
        analysis = await db.analyses.find_one({"_id": ObjectId(analysis_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid analysis"
        )
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )
    
    # Increment view count
    await db.shares.update_one(
        {"share_token": share_token},
        {"$inc": {"view_count": 1}}
    )
    
    return AnalysisDetail(
        id=str(analysis["_id"]),
        website_url=analysis["website_url"],
        status=analysis["status"],
        overall_score=analysis.get("overall_score"),
        ux_analysis=analysis.get("ux_analysis"),
        seo_analysis=analysis.get("seo_analysis"),
        performance_analysis=analysis.get("performance_analysis"),
        content_analysis=analysis.get("content_analysis"),
        ai_summary=analysis.get("ai_summary"),
        priority_recommendations=analysis.get("priority_recommendations"),
        action_plan=analysis.get("action_plan"),
        screenshot_url=analysis.get("screenshot_url"),
        pdf_url=analysis.get("pdf_url"),
        created_at=analysis["created_at"],
        completed_at=analysis.get("completed_at")
    )


@router.delete("/{share_token}")
async def revoke_share_link(
    share_token: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """Revoke a share link"""
    db = get_database()
    
    share = await db.shares.find_one({"share_token": share_token})
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    # Check ownership
    if current_user and share.get('created_by') != current_user.get('user_id'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this share link"
        )
    
    # Deactivate share
    await db.shares.update_one(
        {"share_token": share_token},
        {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
    )
    
    return {"message": "Share link revoked successfully"}


@router.get("/{analysis_id}/shares")
async def list_share_links(
    analysis_id: str,
    current_user: Optional[dict] = Depends(get_current_user)
):
    """List all share links for an analysis"""
    db = get_database()
    
    shares = await db.shares.find({"analysis_id": analysis_id}).to_list(length=100)
    
    return {
        "shares": [
            {
                "share_token": share["share_token"],
                "share_url": f"/share/{share['share_token']}",
                "created_at": share["created_at"],
                "expires_at": share["expires_at"],
                "view_count": share.get("view_count", 0),
                "is_active": share.get("is_active", True)
            }
            for share in shares
        ]
    }
