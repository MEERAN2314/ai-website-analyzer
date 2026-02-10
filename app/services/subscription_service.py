from datetime import datetime, timedelta
from typing import Dict, Optional
from bson import ObjectId

from app.models.subscription import Subscription, SubscriptionStatus, BillingHistory
from app.schemas.subscription import PlanDetails, PlanLimits


class SubscriptionService:
    """Service for managing subscriptions and pricing"""
    
    # Plan configurations
    PLANS = {
        "free": PlanDetails(
            name="free",
            display_name="Free",
            description="Perfect for trying out our platform",
            price_monthly=0.0,
            price_yearly=0.0,
            limits=PlanLimits(
                analyses_limit=10,
                comparisons_limit=0,
                exports_limit=5,
                ai_chat=True,
                priority_support=False,
                custom_reports=False,
                api_access=False
            ),
            features=[
                "10 website analyses per month",
                "Basic AI insights",
                "5 PDF exports",
                "Email support"
            ],
            is_popular=False
        ),
        "basic": PlanDetails(
            name="basic",
            display_name="Basic",
            description="Great for small businesses and freelancers",
            price_monthly=499.0,
            price_yearly=4990.0,  # ~₹416/month (2 months free)
            limits=PlanLimits(
                analyses_limit=50,
                comparisons_limit=10,
                exports_limit=50,
                ai_chat=True,
                priority_support=False,
                custom_reports=False,
                api_access=False
            ),
            features=[
                "50 website analyses per month",
                "10 competitor comparisons",
                "Unlimited PDF exports",
                "Advanced AI insights",
                "Email support",
                "Share analysis links"
            ],
            is_popular=False
        ),
        "pro": PlanDetails(
            name="pro",
            display_name="Pro",
            description="Best for growing agencies and teams",
            price_monthly=1999.0,
            price_yearly=19990.0,  # ~₹1666/month (2 months free)
            limits=PlanLimits(
                analyses_limit=200,
                comparisons_limit=50,
                exports_limit=-1,  # Unlimited
                ai_chat=True,
                priority_support=True,
                custom_reports=True,
                api_access=False
            ),
            features=[
                "200 website analyses per month",
                "50 competitor comparisons",
                "Unlimited exports",
                "Advanced AI insights",
                "Priority email support",
                "Custom branded reports",
                "Share analysis links",
                "30/60/90 day action plans"
            ],
            is_popular=True
        ),
        "enterprise": PlanDetails(
            name="enterprise",
            display_name="Enterprise",
            description="For large organizations with custom needs",
            price_monthly=4999.0,
            price_yearly=49990.0,  # ~₹4166/month (2 months free)
            limits=PlanLimits(
                analyses_limit=-1,  # Unlimited
                comparisons_limit=-1,  # Unlimited
                exports_limit=-1,  # Unlimited
                ai_chat=True,
                priority_support=True,
                custom_reports=True,
                api_access=True
            ),
            features=[
                "Unlimited website analyses",
                "Unlimited competitor comparisons",
                "Unlimited exports",
                "Advanced AI insights",
                "24/7 priority support",
                "Custom branded reports",
                "API access",
                "Dedicated account manager",
                "Custom integrations",
                "SLA guarantee"
            ],
            is_popular=False
        )
    }
    
    @classmethod
    def get_plan_details(cls, plan_name: str) -> Optional[PlanDetails]:
        """Get plan details by name"""
        return cls.PLANS.get(plan_name.lower())
    
    @classmethod
    def get_all_plans(cls) -> Dict[str, PlanDetails]:
        """Get all available plans"""
        return cls.PLANS
    
    @classmethod
    async def create_subscription(
        cls,
        db,
        user_id: str,
        plan: str,
        billing_cycle: str = "monthly"
    ) -> Subscription:
        """Create a new subscription with 30-day free trial"""
        
        plan_details = cls.get_plan_details(plan)
        if not plan_details:
            raise ValueError(f"Invalid plan: {plan}")
        
        # Calculate trial period (30 days)
        trial_start = datetime.utcnow()
        trial_end = trial_start + timedelta(days=30)
        
        # Calculate pricing (100% off for first month)
        original_price = plan_details.price_monthly if billing_cycle == "monthly" else plan_details.price_yearly
        discount = 100.0
        final_price = 0.0
        
        # Create subscription
        subscription = Subscription(
            user_id=user_id,
            plan=plan,
            status=SubscriptionStatus.TRIAL,
            is_trial=True,
            trial_start_date=trial_start,
            trial_end_date=trial_end,
            start_date=trial_start,
            next_billing_date=trial_end,
            original_price=original_price,
            discount_percentage=discount,
            final_price=final_price,
            analyses_limit=plan_details.limits.analyses_limit,
            comparisons_limit=plan_details.limits.comparisons_limit,
            exports_limit=plan_details.limits.exports_limit,
            analyses_used=0,
            comparisons_used=0,
            exports_used=0
        )
        
        # Save to database
        result = await db.subscriptions.insert_one(subscription.dict(by_alias=True, exclude={"id"}))
        subscription.id = result.inserted_id
        
        # Create billing history entry
        billing_entry = BillingHistory(
            user_id=user_id,
            subscription_id=str(subscription.id),
            transaction_type="trial_start",
            to_plan=plan,
            amount=original_price,
            discount=original_price,  # 100% discount
            final_amount=0.0,
            status="completed",
            description=f"Started {plan_details.display_name} plan with 30-day free trial"
        )
        await db.billing_history.insert_one(billing_entry.dict(by_alias=True, exclude={"id"}))
        
        # Update user plan
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"plan": plan, "updated_at": datetime.utcnow()}}
        )
        
        return subscription
    
    @classmethod
    async def get_user_subscription(cls, db, user_id: str) -> Optional[Subscription]:
        """Get active subscription for user"""
        subscription_data = await db.subscriptions.find_one({
            "user_id": user_id,
            "status": {"$in": [SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE, SubscriptionStatus.GRACE_PERIOD]}
        })
        
        if subscription_data:
            return Subscription(**subscription_data)
        return None
    
    @classmethod
    async def check_usage_limit(cls, db, user_id: str, usage_type: str) -> tuple[bool, str]:
        """
        Check if user can perform action based on usage limits
        Returns: (can_perform, message)
        """
        subscription = await cls.get_user_subscription(db, user_id)
        
        if not subscription:
            return False, "No active subscription found"
        
        # Check if trial/subscription expired
        if subscription.status == SubscriptionStatus.EXPIRED:
            return False, "Your subscription has expired. Please upgrade to continue."
        
        # Check specific usage limits
        if usage_type == "analysis":
            if subscription.analyses_limit == -1:  # Unlimited
                return True, ""
            if subscription.analyses_used >= subscription.analyses_limit:
                return False, f"You've reached your monthly limit of {subscription.analyses_limit} analyses. Upgrade for more!"
        
        elif usage_type == "comparison":
            if subscription.comparisons_limit == -1:  # Unlimited
                return True, ""
            if subscription.comparisons_limit == 0:
                return False, "Competitor comparisons are not available in your plan. Upgrade to access this feature!"
            if subscription.comparisons_used >= subscription.comparisons_limit:
                return False, f"You've reached your monthly limit of {subscription.comparisons_limit} comparisons. Upgrade for more!"
        
        elif usage_type == "export":
            if subscription.exports_limit == -1:  # Unlimited
                return True, ""
            if subscription.exports_used >= subscription.exports_limit:
                return False, f"You've reached your monthly limit of {subscription.exports_limit} exports. Upgrade for more!"
        
        return True, ""
    
    @classmethod
    async def increment_usage(cls, db, user_id: str, usage_type: str):
        """Increment usage counter"""
        subscription = await cls.get_user_subscription(db, user_id)
        
        if not subscription:
            return
        
        update_field = f"{usage_type}s_used"
        await db.subscriptions.update_one(
            {"_id": subscription.id},
            {
                "$inc": {update_field: 1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
    
    @classmethod
    async def upgrade_plan(cls, db, user_id: str, new_plan: str) -> Subscription:
        """Upgrade user to a new plan"""
        current_subscription = await cls.get_user_subscription(db, user_id)
        
        if not current_subscription:
            # Create new subscription
            return await cls.create_subscription(db, user_id, new_plan)
        
        # Cancel current subscription
        await db.subscriptions.update_one(
            {"_id": current_subscription.id},
            {
                "$set": {
                    "status": SubscriptionStatus.CANCELLED,
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Create new subscription
        new_subscription = await cls.create_subscription(db, user_id, new_plan)
        
        # Create billing history
        plan_details = cls.get_plan_details(new_plan)
        billing_entry = BillingHistory(
            user_id=user_id,
            subscription_id=str(new_subscription.id),
            transaction_type="upgrade",
            from_plan=current_subscription.plan,
            to_plan=new_plan,
            amount=plan_details.price_monthly,
            discount=plan_details.price_monthly,  # 100% off for trial
            final_amount=0.0,
            status="completed",
            description=f"Upgraded from {current_subscription.plan} to {new_plan} with 30-day free trial"
        )
        await db.billing_history.insert_one(billing_entry.dict(by_alias=True, exclude={"id"}))
        
        return new_subscription
    
    @classmethod
    async def check_expired_trials(cls, db):
        """Check and update expired trials (run as scheduled task)"""
        now = datetime.utcnow()
        
        # Find expired trials
        expired_trials = await db.subscriptions.find({
            "status": SubscriptionStatus.TRIAL,
            "trial_end_date": {"$lt": now}
        }).to_list(length=1000)
        
        for subscription_data in expired_trials:
            subscription = Subscription(**subscription_data)
            
            # Move to grace period (7 days)
            grace_end = now + timedelta(days=7)
            await db.subscriptions.update_one(
                {"_id": subscription.id},
                {
                    "$set": {
                        "status": SubscriptionStatus.GRACE_PERIOD,
                        "end_date": grace_end,
                        "updated_at": now
                    }
                }
            )
            
            # TODO: Send email notification about trial expiry
            print(f"Trial expired for user {subscription.user_id}, moved to grace period")
        
        # Find expired grace periods
        expired_grace = await db.subscriptions.find({
            "status": SubscriptionStatus.GRACE_PERIOD,
            "end_date": {"$lt": now}
        }).to_list(length=1000)
        
        for subscription_data in expired_grace:
            subscription = Subscription(**subscription_data)
            
            # Downgrade to free plan
            await db.subscriptions.update_one(
                {"_id": subscription.id},
                {
                    "$set": {
                        "status": SubscriptionStatus.EXPIRED,
                        "updated_at": now
                    }
                }
            )
            
            # Create free plan subscription
            await cls.create_subscription(db, subscription.user_id, "free")
            
            # TODO: Send email notification about downgrade
            print(f"Grace period expired for user {subscription.user_id}, downgraded to free")
