from fastapi import HTTPException, status
from datetime import datetime, timedelta
from app.core.config import settings


async def check_rate_limit(user_id: str, plan: str, db):
    """Check if user has exceeded rate limit"""
    
    # Get rate limits based on plan
    rate_limits = {
        "free": settings.RATE_LIMIT_FREE_USER,
        "basic": settings.RATE_LIMIT_BASIC_USER,
        "pro": settings.RATE_LIMIT_PRO_USER,
        "enterprise": settings.RATE_LIMIT_ENTERPRISE_USER
    }
    
    limit = rate_limits.get(plan, settings.RATE_LIMIT_FREE_USER)
    
    if user_id:
        # Get user's monthly count
        user = await db.users.find_one({"_id": user_id})
        if user:
            monthly_reset_date = user.get("monthly_reset_date")
            
            # Reset if needed
            if not monthly_reset_date or monthly_reset_date < datetime.utcnow():
                await db.users.update_one(
                    {"_id": user_id},
                    {
                        "$set": {
                            "monthly_analyses_count": 0,
                            "monthly_reset_date": datetime.utcnow() + timedelta(days=30)
                        }
                    }
                )
                monthly_count = 0
            else:
                monthly_count = user.get("monthly_analyses_count", 0)
            
            # Check limit
            if monthly_count >= limit:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Monthly analysis limit reached. Upgrade your plan for more analyses."
                )
            
            # Increment count
            await db.users.update_one(
                {"_id": user_id},
                {"$inc": {"monthly_analyses_count": 1, "analyses_count": 1}}
            )
    else:
        # Guest user - always limited to 1
        if limit <= 0:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Please register to perform more analyses"
            )
