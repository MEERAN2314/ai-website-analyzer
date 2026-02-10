from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PlanLimits(BaseModel):
    """Plan limits and features"""
    analyses_limit: int
    comparisons_limit: int
    exports_limit: int
    ai_chat: bool
    priority_support: bool
    custom_reports: bool
    api_access: bool


class PlanDetails(BaseModel):
    """Plan pricing and details"""
    name: str
    display_name: str
    description: str
    price_monthly: float
    price_yearly: float
    limits: PlanLimits
    features: list[str]
    is_popular: bool = False


class SubscriptionCreate(BaseModel):
    """Create new subscription"""
    plan: str = Field(..., description="Plan name: free, basic, pro, enterprise")
    billing_cycle: str = Field(default="monthly", description="monthly or yearly")


class SubscriptionResponse(BaseModel):
    """Subscription response"""
    id: str
    user_id: str
    plan: str
    status: str
    is_trial: bool
    trial_end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    analyses_used: int
    analyses_limit: int
    comparisons_used: int
    comparisons_limit: int
    exports_used: int
    exports_limit: int
    created_at: datetime


class SubscriptionUpdate(BaseModel):
    """Update subscription"""
    plan: Optional[str] = None
    status: Optional[str] = None


class UsageStats(BaseModel):
    """User usage statistics"""
    analyses_used: int
    analyses_limit: int
    analyses_remaining: int
    comparisons_used: int
    comparisons_limit: int
    comparisons_remaining: int
    exports_used: int
    exports_limit: int
    exports_remaining: int
    plan: str
    status: str
    is_trial: bool
    days_remaining: Optional[int] = None
