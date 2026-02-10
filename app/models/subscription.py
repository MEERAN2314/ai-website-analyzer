from datetime import datetime
from typing import Optional, Annotated
from pydantic import BaseModel, Field, BeforeValidator
from bson import ObjectId


def validate_object_id(v):
    """Validate ObjectId"""
    if isinstance(v, ObjectId):
        return v
    if ObjectId.is_valid(v):
        return ObjectId(v)
    raise ValueError("Invalid ObjectId")


PyObjectId = Annotated[ObjectId, BeforeValidator(validate_object_id)]


class SubscriptionStatus:
    TRIAL = "trial"
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    GRACE_PERIOD = "grace_period"


class Subscription(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    plan: str  # free, basic, pro, enterprise
    status: str = SubscriptionStatus.TRIAL
    
    # Trial information
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    is_trial: bool = True
    
    # Subscription dates
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    next_billing_date: Optional[datetime] = None
    
    # Pricing
    original_price: float = 0.0
    discount_percentage: float = 100.0  # 100% off for first month
    final_price: float = 0.0
    
    # Usage limits (based on plan)
    analyses_limit: int = 10
    comparisons_limit: int = 0
    exports_limit: int = 5
    
    # Usage tracking
    analyses_used: int = 0
    comparisons_used: int = 0
    exports_used: int = 0
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    cancelled_at: Optional[datetime] = None
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }


class BillingHistory(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: str
    subscription_id: str
    
    # Transaction details
    transaction_type: str  # upgrade, downgrade, renewal, cancellation
    from_plan: Optional[str] = None
    to_plan: str
    
    # Pricing
    amount: float = 0.0
    discount: float = 0.0
    final_amount: float = 0.0
    
    # Status
    status: str = "completed"  # completed, pending, failed
    
    # Metadata
    description: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }
