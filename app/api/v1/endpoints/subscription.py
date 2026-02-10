from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from datetime import datetime

from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    UsageStats,
    PlanDetails
)
from app.core.security import get_current_user
from app.core.database import get_database
from app.services.subscription_service import SubscriptionService
from app.models.subscription import SubscriptionStatus

router = APIRouter()


@router.get("/plans")
async def get_plans():
    """Get all available plans"""
    plans = SubscriptionService.get_all_plans()
    return {
        "plans": [plan.dict() for plan in plans.values()]
    }


@router.get("/plans/{plan_name}")
async def get_plan_details(plan_name: str):
    """Get details for a specific plan"""
    plan = SubscriptionService.get_plan_details(plan_name)
    
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan '{plan_name}' not found"
        )
    
    return plan.dict()


@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new subscription (30-day free trial)"""
    db = get_database()
    user_id = current_user.get("user_id")
    
    # Check if user already has an active subscription
    existing_subscription = await SubscriptionService.get_user_subscription(db, user_id)
    
    if existing_subscription and existing_subscription.status in [
        SubscriptionStatus.TRIAL,
        SubscriptionStatus.ACTIVE
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have an active subscription. Use the upgrade endpoint to change plans."
        )
    
    # Create subscription
    try:
        subscription = await SubscriptionService.create_subscription(
            db,
            user_id,
            subscription_data.plan,
            subscription_data.billing_cycle
        )
        
        return SubscriptionResponse(
            id=str(subscription.id),
            user_id=subscription.user_id,
            plan=subscription.plan,
            status=subscription.status,
            is_trial=subscription.is_trial,
            trial_end_date=subscription.trial_end_date,
            next_billing_date=subscription.next_billing_date,
            analyses_used=subscription.analyses_used,
            analyses_limit=subscription.analyses_limit,
            comparisons_used=subscription.comparisons_used,
            comparisons_limit=subscription.comparisons_limit,
            exports_used=subscription.exports_used,
            exports_limit=subscription.exports_limit,
            created_at=subscription.created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """Get current user's subscription"""
    db = get_database()
    user_id = current_user.get("user_id")
    
    subscription = await SubscriptionService.get_user_subscription(db, user_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    return SubscriptionResponse(
        id=str(subscription.id),
        user_id=subscription.user_id,
        plan=subscription.plan,
        status=subscription.status,
        is_trial=subscription.is_trial,
        trial_end_date=subscription.trial_end_date,
        next_billing_date=subscription.next_billing_date,
        analyses_used=subscription.analyses_used,
        analyses_limit=subscription.analyses_limit,
        comparisons_used=subscription.comparisons_used,
        comparisons_limit=subscription.comparisons_limit,
        exports_used=subscription.exports_used,
        exports_limit=subscription.exports_limit,
        created_at=subscription.created_at
    )


@router.get("/usage", response_model=UsageStats)
async def get_usage_stats(current_user: dict = Depends(get_current_user)):
    """Get current usage statistics"""
    db = get_database()
    user_id = current_user.get("user_id")
    
    subscription = await SubscriptionService.get_user_subscription(db, user_id)
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    # Calculate remaining days
    days_remaining = None
    if subscription.is_trial and subscription.trial_end_date:
        delta = subscription.trial_end_date - datetime.utcnow()
        days_remaining = max(0, delta.days)
    
    # Calculate remaining usage
    analyses_remaining = -1 if subscription.analyses_limit == -1 else max(0, subscription.analyses_limit - subscription.analyses_used)
    comparisons_remaining = -1 if subscription.comparisons_limit == -1 else max(0, subscription.comparisons_limit - subscription.comparisons_used)
    exports_remaining = -1 if subscription.exports_limit == -1 else max(0, subscription.exports_limit - subscription.exports_used)
    
    return UsageStats(
        analyses_used=subscription.analyses_used,
        analyses_limit=subscription.analyses_limit,
        analyses_remaining=analyses_remaining,
        comparisons_used=subscription.comparisons_used,
        comparisons_limit=subscription.comparisons_limit,
        comparisons_remaining=comparisons_remaining,
        exports_used=subscription.exports_used,
        exports_limit=subscription.exports_limit,
        exports_remaining=exports_remaining,
        plan=subscription.plan,
        status=subscription.status,
        is_trial=subscription.is_trial,
        days_remaining=days_remaining
    )


@router.post("/upgrade/{new_plan}", response_model=SubscriptionResponse)
async def upgrade_subscription(
    new_plan: str,
    current_user: dict = Depends(get_current_user)
):
    """Upgrade to a new plan"""
    db = get_database()
    user_id = current_user.get("user_id")
    
    # Validate plan
    plan_details = SubscriptionService.get_plan_details(new_plan)
    if not plan_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan: {new_plan}"
        )
    
    try:
        subscription = await SubscriptionService.upgrade_plan(db, user_id, new_plan)
        
        return SubscriptionResponse(
            id=str(subscription.id),
            user_id=subscription.user_id,
            plan=subscription.plan,
            status=subscription.status,
            is_trial=subscription.is_trial,
            trial_end_date=subscription.trial_end_date,
            next_billing_date=subscription.next_billing_date,
            analyses_used=subscription.analyses_used,
            analyses_limit=subscription.analyses_limit,
            comparisons_used=subscription.comparisons_used,
            comparisons_limit=subscription.comparisons_limit,
            exports_used=subscription.exports_used,
            exports_limit=subscription.exports_limit,
            created_at=subscription.created_at
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upgrade subscription: {str(e)}"
        )


@router.get("/billing-history")
async def get_billing_history(current_user: dict = Depends(get_current_user)):
    """Get billing history for current user"""
    db = get_database()
    user_id = current_user.get("user_id")
    
    history = await db.billing_history.find(
        {"user_id": user_id}
    ).sort("created_at", -1).to_list(length=100)
    
    return {
        "billing_history": [
            {
                "id": str(entry["_id"]),
                "transaction_type": entry["transaction_type"],
                "from_plan": entry.get("from_plan"),
                "to_plan": entry["to_plan"],
                "amount": entry["amount"],
                "discount": entry["discount"],
                "final_amount": entry["final_amount"],
                "status": entry["status"],
                "description": entry["description"],
                "created_at": entry["created_at"]
            }
            for entry in history
        ]
    }
