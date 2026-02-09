from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime, timedelta
from bson import ObjectId

from app.core.security import get_current_user
from app.core.database import get_database
from app.schemas.analysis import AnalysisResponse

router = APIRouter()


@router.get("/")
async def get_dashboard(current_user: dict = Depends(get_current_user)):
    """Get user dashboard data"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get user data
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get analyses count
    total_analyses = await db.analyses.count_documents({"user_id": user_id})
    
    # Get recent analyses
    recent_analyses = await db.analyses.find(
        {"user_id": user_id}
    ).sort("created_at", -1).limit(5).to_list(length=5)
    
    # Calculate stats
    completed_analyses = await db.analyses.count_documents({
        "user_id": user_id,
        "status": "completed"
    })
    
    # Get average score
    pipeline = [
        {"$match": {"user_id": user_id, "status": "completed"}},
        {"$group": {"_id": None, "avg_score": {"$avg": "$overall_score"}}}
    ]
    avg_result = await db.analyses.aggregate(pipeline).to_list(length=1)
    avg_score = avg_result[0]["avg_score"] if avg_result else 0
    
    return {
        "user": {
            "email": user["email"],
            "full_name": user.get("full_name"),
            "plan": user.get("plan", "free"),
            "analyses_count": total_analyses,
            "monthly_analyses_count": user.get("monthly_analyses_count", 0)
        },
        "stats": {
            "total_analyses": total_analyses,
            "completed_analyses": completed_analyses,
            "average_score": round(avg_score, 2) if avg_score else 0
        },
        "recent_analyses": [
            {
                "id": str(a["_id"]),
                "website_url": a["website_url"],
                "status": a["status"],
                "overall_score": a.get("overall_score"),
                "created_at": a["created_at"]
            }
            for a in recent_analyses
        ]
    }


@router.get("/analyses", response_model=List[AnalysisResponse])
async def get_user_analyses(
    skip: int = 0,
    limit: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """Get all user analyses"""
    db = get_database()
    user_id = current_user["user_id"]
    
    analyses = await db.analyses.find(
        {"user_id": user_id}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    
    return [
        AnalysisResponse(
            id=str(a["_id"]),
            website_url=a["website_url"],
            status=a["status"],
            overall_score=a.get("overall_score"),
            created_at=a["created_at"],
            completed_at=a.get("completed_at")
        )
        for a in analyses
    ]


@router.get("/stats")
async def get_user_stats(current_user: dict = Depends(get_current_user)):
    """Get detailed user statistics"""
    db = get_database()
    user_id = current_user["user_id"]
    
    # Get analyses by status
    status_counts = {}
    for status_type in ["pending", "processing", "completed", "failed"]:
        count = await db.analyses.count_documents({
            "user_id": user_id,
            "status": status_type
        })
        status_counts[status_type] = count
    
    # Get analyses over time (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    daily_analyses = await db.analyses.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "created_at": {"$gte": thirty_days_ago}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]).to_list(length=30)
    
    # Get score distribution
    score_distribution = await db.analyses.aggregate([
        {
            "$match": {
                "user_id": user_id,
                "status": "completed",
                "overall_score": {"$exists": True}
            }
        },
        {
            "$bucket": {
                "groupBy": "$overall_score",
                "boundaries": [0, 20, 40, 60, 80, 100],
                "default": "Other",
                "output": {"count": {"$sum": 1}}
            }
        }
    ]).to_list(length=10)
    
    return {
        "status_counts": status_counts,
        "daily_analyses": [
            {"date": item["_id"], "count": item["count"]}
            for item in daily_analyses
        ],
        "score_distribution": score_distribution
    }
