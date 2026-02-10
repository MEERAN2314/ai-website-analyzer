from fastapi import APIRouter, HTTPException, status, Depends
from bson import ObjectId
from datetime import datetime, timedelta
import secrets
from typing import Optional

from app.schemas.analysis import AnalysisDetail
from app.core.security import get_current_user
from app.core.database import get_database

router = APIRouter()


# ==================== COMPARISON SHARING ====================

@router.post("/comparison/{comparison_id}/share")
async def create_comparison_share_link(
    comparison_id: str,
    expires_in_days: int = 30,
    password: Optional[str] = None
):
    """
    Create a shareable link for comparison analysis
    
    - **comparison_id**: The comparison ID
    - **expires_in_days**: Number of days until link expires (default: 30)
    - **password**: Optional password protection
    """
    db = get_database()
    
    try:
        comparison = await db.comparisons.find_one({"_id": ObjectId(comparison_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comparison ID"
        )
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )
    
    if comparison.get("status") != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot share incomplete comparison"
        )
    
    # Generate unique share token
    share_token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
    
    # Hash password if provided
    password_hash = None
    if password:
        from app.core.security import get_password_hash
        password_hash = get_password_hash(password)
    
    # Create share record
    share_data = {
        "comparison_id": comparison_id,
        "share_token": share_token,
        "created_at": datetime.utcnow(),
        "expires_at": expires_at,
        "view_count": 0,
        "is_active": True,
        "password_hash": password_hash,
        "type": "comparison"
    }
    
    result = await db.shares.insert_one(share_data)
    
    # Update comparison with share info
    await db.comparisons.update_one(
        {"_id": ObjectId(comparison_id)},
        {"$set": {"is_shared": True, "last_shared_at": datetime.utcnow()}}
    )
    
    share_url = f"/share/comparison/{share_token}"
    full_url = f"http://localhost:8000{share_url}"  # Update with your domain
    
    return {
        "share_id": str(result.inserted_id),
        "share_token": share_token,
        "share_url": share_url,
        "full_url": full_url,
        "expires_at": expires_at,
        "has_password": password is not None,
        "message": "Share link created successfully"
    }


@router.get("/comparison/{share_token}")
async def get_shared_comparison(share_token: str, password: Optional[str] = None):
    """
    Get comparison via share link
    
    - **share_token**: The share token
    - **password**: Password if link is protected
    """
    db = get_database()
    
    # Find share record
    share = await db.shares.find_one({
        "share_token": share_token,
        "type": "comparison"
    })
    
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
    
    # Check password if required
    if share.get('password_hash'):
        if not password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password required"
            )
        
        from app.core.security import verify_password
        if not verify_password(password, share['password_hash']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
    
    # Get comparison
    comparison_id = share.get('comparison_id')
    try:
        comparison = await db.comparisons.find_one({"_id": ObjectId(comparison_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comparison"
        )
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )
    
    # Increment view count
    await db.shares.update_one(
        {"share_token": share_token},
        {
            "$inc": {"view_count": 1},
            "$set": {"last_viewed_at": datetime.utcnow()}
        }
    )
    
    # Convert ObjectId to string
    comparison["_id"] = str(comparison["_id"])
    
    return comparison


@router.delete("/comparison/{share_token}")
async def revoke_comparison_share_link(share_token: str):
    """
    Revoke a comparison share link
    
    - **share_token**: The share token
    """
    db = get_database()
    
    share = await db.shares.find_one({
        "share_token": share_token,
        "type": "comparison"
    })
    
    if not share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Share link not found"
        )
    
    # Deactivate share
    await db.shares.update_one(
        {"share_token": share_token},
        {"$set": {"is_active": False, "revoked_at": datetime.utcnow()}}
    )
    
    return {"message": "Share link revoked successfully"}


# ==================== ANALYSIS SHARING ====================


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
        security_analysis=analysis.get("security_analysis"),
        image_analysis=analysis.get("image_analysis"),
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
