"""
Subscription Management Backend
Handles subscription plans, upgrades, billing, and feature access control
"""

from fastapi import HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from enum import Enum
import uuid
import logging

logger = logging.getLogger(__name__)

class SubscriptionPlan(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TRIAL = "trial"

class BillingCycle(str, Enum):
    FREE = "free"
    MONTHLY = "monthly"
    YEARLY = "yearly"

# Subscription plan configurations
SUBSCRIPTION_PLANS = {
    SubscriptionPlan.BASIC: {
        "id": "basic",
        "name": "Basic",
        "price_monthly": 0,
        "price_yearly": 0,
        "features": {
            "BASIC_SEARCH": True,
            "BASIC_LISTINGS": True,
            "BASIC_PROFILE": True,
            "CONTACT_TRADERS": True,
        },
        "limits": {
            "listings_per_month": 5,
            "connections_per_month": 10,
            "search_results": 20,
            "exports_per_month": 0,
            "api_calls_per_day": 100,
        },
        "description": "Perfect for getting started in oil & gas trading"
    },
    SubscriptionPlan.PREMIUM: {
        "id": "premium",
        "name": "Premium",
        "price_monthly": 19,
        "price_yearly": 190,  # 2 months free
        "features": {
            "BASIC_SEARCH": True,
            "BASIC_LISTINGS": True,
            "BASIC_PROFILE": True,
            "CONTACT_TRADERS": True,
            "ADVANCED_SEARCH": True,
            "UNLIMITED_LISTINGS": True,
            "MARKET_ANALYTICS": True,
            "PRICE_ALERTS": True,
            "EXPORT_DATA": True,
            "PRIORITY_LISTINGS": True,
        },
        "limits": {
            "listings_per_month": -1,  # unlimited
            "connections_per_month": 100,
            "search_results": 100,
            "exports_per_month": 50,
            "api_calls_per_day": 1000,
        },
        "description": "Enhanced features for active traders"
    },
    SubscriptionPlan.ENTERPRISE: {
        "id": "enterprise",
        "name": "Enterprise",
        "price_monthly": 45,
        "price_yearly": 450,  # 2 months free
        "features": {
            "BASIC_SEARCH": True,
            "BASIC_LISTINGS": True,
            "BASIC_PROFILE": True,
            "CONTACT_TRADERS": True,
            "ADVANCED_SEARCH": True,
            "UNLIMITED_LISTINGS": True,
            "MARKET_ANALYTICS": True,
            "PRICE_ALERTS": True,
            "EXPORT_DATA": True,
            "PRIORITY_LISTINGS": True,
            "ADVANCED_ANALYTICS": True,
            "API_ACCESS": True,
            "PRIORITY_SUPPORT": True,
            "CUSTOM_BRANDING": True,
            "BULK_OPERATIONS": True,
            "ADVANCED_REPORTING": True,
            "WHITE_LABEL": True,
        },
        "limits": {
            "listings_per_month": -1,
            "connections_per_month": -1,
            "search_results": -1,
            "exports_per_month": -1,
            "api_calls_per_day": 10000,
        },
        "description": "Complete solution for enterprise trading operations"
    }
}

# Pydantic models
class SubscriptionCreate(BaseModel):
    plan_id: SubscriptionPlan
    billing_cycle: BillingCycle = BillingCycle.MONTHLY
    payment_method_id: Optional[str] = None

class SubscriptionUpdate(BaseModel):
    plan_id: Optional[SubscriptionPlan] = None
    billing_cycle: Optional[BillingCycle] = None
    auto_renew: Optional[bool] = None

class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    billing_cycle: BillingCycle
    current_period_start: datetime
    current_period_end: datetime
    auto_renew: bool
    created_at: datetime
    updated_at: datetime

class UsageStats(BaseModel):
    listings_used: int = 0
    connections_used: int = 0
    searches_performed: int = 0
    exports_used: int = 0
    api_calls_used: int = 0
    period_start: datetime
    period_end: datetime

class FeatureAccess(BaseModel):
    feature: str
    has_access: bool
    plan_required: Optional[str] = None

class SubscriptionManager:
    """Manages subscription operations and feature access"""
    
    def __init__(self, users_collection, subscriptions_collection, usage_collection):
        self.users_collection = users_collection
        self.subscriptions_collection = subscriptions_collection
        self.usage_collection = usage_collection
    
    async def create_subscription(self, user_id: str, subscription_data: SubscriptionCreate) -> SubscriptionResponse:
        """Create a new subscription for a user"""
        try:
            # Check if user already has an active subscription
            existing_subscription = self.subscriptions_collection.find_one({
                "user_id": user_id,
                "status": {"$in": [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]}
            })
            
            if existing_subscription:
                raise HTTPException(
                    status_code=400,
                    detail="User already has an active subscription"
                )
            
            # Get plan details
            plan_info = SUBSCRIPTION_PLANS.get(subscription_data.plan_id)
            if not plan_info:
                raise HTTPException(status_code=400, detail="Invalid subscription plan")
            
            # Calculate subscription period
            current_period_start = datetime.utcnow()
            if subscription_data.billing_cycle == BillingCycle.YEARLY:
                current_period_end = current_period_start + timedelta(days=365)
            elif subscription_data.billing_cycle == BillingCycle.MONTHLY:
                current_period_end = current_period_start + timedelta(days=30)
            else:  # FREE
                current_period_end = datetime(2099, 12, 31)  # Far future for free plans
            
            # Create subscription document
            subscription_id = str(uuid.uuid4())
            subscription_doc = {
                "subscription_id": subscription_id,
                "user_id": user_id,
                "plan": subscription_data.plan_id,
                "status": SubscriptionStatus.ACTIVE,
                "billing_cycle": subscription_data.billing_cycle,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end,
                "auto_renew": True,
                "payment_method_id": subscription_data.payment_method_id,
                "created_at": current_period_start,
                "updated_at": current_period_start,
                "trial_end": None,
                "cancelled_at": None,
            }
            
            # Insert subscription
            self.subscriptions_collection.insert_one(subscription_doc)
            
            # Update user's subscription status
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"subscription_plan": subscription_data.plan_id}}
            )
            
            # Initialize usage stats
            await self._initialize_usage_stats(user_id, current_period_start, current_period_end)
            
            logger.info(f"Created subscription {subscription_id} for user {user_id}")
            
            return SubscriptionResponse(**subscription_doc)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to create subscription")
    
    async def get_user_subscription(self, user_id: str) -> Optional[SubscriptionResponse]:
        """Get user's current subscription"""
        try:
            subscription = self.subscriptions_collection.find_one({
                "user_id": user_id,
                "status": {"$in": [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]}
            })
            
            if subscription:
                return SubscriptionResponse(**subscription)
            
            # Return default basic subscription if none exists
            return SubscriptionResponse(
                subscription_id="default",
                user_id=user_id,
                plan=SubscriptionPlan.BASIC,
                status=SubscriptionStatus.ACTIVE,
                billing_cycle=BillingCycle.FREE,
                current_period_start=datetime.utcnow(),
                current_period_end=datetime(2099, 12, 31),
                auto_renew=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Error getting user subscription: {e}")
            return None
    
    async def upgrade_subscription(self, user_id: str, new_plan: SubscriptionPlan, 
                                 billing_cycle: BillingCycle = BillingCycle.MONTHLY) -> SubscriptionResponse:
        """Upgrade user's subscription to a higher plan"""
        try:
            current_subscription = await self.get_user_subscription(user_id)
            
            if not current_subscription:
                raise HTTPException(status_code=404, detail="No subscription found")
            
            # Validate upgrade path
            plan_hierarchy = {
                SubscriptionPlan.BASIC: 0,
                SubscriptionPlan.PREMIUM: 1,
                SubscriptionPlan.ENTERPRISE: 2
            }
            
            current_level = plan_hierarchy.get(current_subscription.plan, 0)
            new_level = plan_hierarchy.get(new_plan, 0)
            
            if new_level <= current_level and current_subscription.plan != SubscriptionPlan.BASIC:
                raise HTTPException(status_code=400, detail="Can only upgrade to higher plans")
            
            # Calculate new subscription period
            current_period_start = datetime.utcnow()
            if billing_cycle == BillingCycle.YEARLY:
                current_period_end = current_period_start + timedelta(days=365)
            else:
                current_period_end = current_period_start + timedelta(days=30)
            
            # Update subscription
            update_data = {
                "plan": new_plan,
                "billing_cycle": billing_cycle,
                "current_period_start": current_period_start,
                "current_period_end": current_period_end,
                "updated_at": current_period_start,
                "status": SubscriptionStatus.ACTIVE
            }
            
            self.subscriptions_collection.update_one(
                {"user_id": user_id, "status": {"$in": [SubscriptionStatus.ACTIVE, SubscriptionStatus.TRIAL]}},
                {"$set": update_data}
            )
            
            # Update user's subscription plan
            self.users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"subscription_plan": new_plan}}
            )
            
            # Reset usage stats for new period
            await self._initialize_usage_stats(user_id, current_period_start, current_period_end)
            
            logger.info(f"Upgraded subscription for user {user_id} to {new_plan}")
            
            # Return updated subscription
            return await self.get_user_subscription(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error upgrading subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to upgrade subscription")
    
    async def cancel_subscription(self, user_id: str) -> SubscriptionResponse:
        """Cancel user's subscription (remains active until period end)"""
        try:
            current_subscription = await self.get_user_subscription(user_id)
            
            if not current_subscription or current_subscription.plan == SubscriptionPlan.BASIC:
                raise HTTPException(status_code=400, detail="No cancellable subscription found")
            
            # Update subscription to cancelled (but keep active until period end)
            self.subscriptions_collection.update_one(
                {"user_id": user_id, "status": SubscriptionStatus.ACTIVE},
                {
                    "$set": {
                        "auto_renew": False,
                        "cancelled_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Cancelled subscription for user {user_id}")
            
            return await self.get_user_subscription(user_id)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error cancelling subscription: {e}")
            raise HTTPException(status_code=500, detail="Failed to cancel subscription")
    
    def check_feature_access(self, user_subscription: SubscriptionResponse, feature: str) -> FeatureAccess:
        """Check if user has access to a specific feature"""
        if not user_subscription:
            return FeatureAccess(feature=feature, has_access=False, plan_required="premium")
        
        plan_info = SUBSCRIPTION_PLANS.get(user_subscription.plan)
        if not plan_info:
            return FeatureAccess(feature=feature, has_access=False, plan_required="premium")
        
        has_access = plan_info["features"].get(feature, False)
        
        if not has_access:
            # Find minimum plan that has this feature
            for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
                if plan_data["features"].get(feature, False):
                    return FeatureAccess(
                        feature=feature, 
                        has_access=False, 
                        plan_required=plan_id
                    )
        
        return FeatureAccess(feature=feature, has_access=has_access)
    
    async def check_usage_limit(self, user_id: str, limit_type: str, increment: int = 1) -> Dict:
        """Check and optionally increment usage against limits"""
        try:
            user_subscription = await self.get_user_subscription(user_id)
            if not user_subscription:
                return {"allowed": False, "reason": "No subscription found"}
            
            plan_info = SUBSCRIPTION_PLANS.get(user_subscription.plan)
            if not plan_info:
                return {"allowed": False, "reason": "Invalid subscription plan"}
            
            limit = plan_info["limits"].get(limit_type, 0)
            
            # Unlimited access
            if limit == -1:
                if increment > 0:
                    await self._increment_usage(user_id, limit_type, increment)
                return {"allowed": True, "limit": -1, "used": -1, "remaining": -1}
            
            # Get current usage
            current_usage = await self._get_current_usage(user_id, limit_type)
            
            # Check if increment would exceed limit
            if current_usage + increment > limit:
                return {
                    "allowed": False,
                    "limit": limit,
                    "used": current_usage,
                    "remaining": max(0, limit - current_usage),
                    "reason": f"Would exceed {limit_type} limit"
                }
            
            # Increment usage if requested
            if increment > 0:
                await self._increment_usage(user_id, limit_type, increment)
                current_usage += increment
            
            return {
                "allowed": True,
                "limit": limit,
                "used": current_usage,
                "remaining": max(0, limit - current_usage)
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limit: {e}")
            return {"allowed": False, "reason": "Error checking usage"}
    
    async def get_usage_stats(self, user_id: str) -> UsageStats:
        """Get user's current usage statistics"""
        try:
            user_subscription = await self.get_user_subscription(user_id)
            if not user_subscription:
                return UsageStats(
                    period_start=datetime.utcnow(),
                    period_end=datetime.utcnow() + timedelta(days=30)
                )
            
            usage_doc = self.usage_collection.find_one({
                "user_id": user_id,
                "period_start": {"$lte": datetime.utcnow()},
                "period_end": {"$gte": datetime.utcnow()}
            })
            
            if usage_doc:
                return UsageStats(**usage_doc)
            
            # Initialize if not found
            await self._initialize_usage_stats(
                user_id,
                user_subscription.current_period_start,
                user_subscription.current_period_end
            )
            
            return UsageStats(
                period_start=user_subscription.current_period_start,
                period_end=user_subscription.current_period_end
            )
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {e}")
            return UsageStats(
                period_start=datetime.utcnow(),
                period_end=datetime.utcnow() + timedelta(days=30)
            )
    
    async def _initialize_usage_stats(self, user_id: str, period_start: datetime, period_end: datetime):
        """Initialize usage statistics for a user"""
        usage_doc = {
            "user_id": user_id,
            "listings_used": 0,
            "connections_used": 0,
            "searches_performed": 0,
            "exports_used": 0,
            "api_calls_used": 0,
            "period_start": period_start,
            "period_end": period_end,
            "created_at": datetime.utcnow()
        }
        
        # Remove any existing usage doc for this period
        self.usage_collection.delete_many({
            "user_id": user_id,
            "period_start": period_start
        })
        
        self.usage_collection.insert_one(usage_doc)
    
    async def _get_current_usage(self, user_id: str, limit_type: str) -> int:
        """Get current usage for a specific limit type"""
        usage_doc = self.usage_collection.find_one({
            "user_id": user_id,
            "period_start": {"$lte": datetime.utcnow()},
            "period_end": {"$gte": datetime.utcnow()}
        })
        
        if not usage_doc:
            return 0
        
        field_mapping = {
            "listings_per_month": "listings_used",
            "connections_per_month": "connections_used",
            "exports_per_month": "exports_used",
            "api_calls_per_day": "api_calls_used"
        }
        
        field_name = field_mapping.get(limit_type, limit_type.replace("_per_month", "_used").replace("_per_day", "_used"))
        return usage_doc.get(field_name, 0)
    
    async def _increment_usage(self, user_id: str, limit_type: str, increment: int):
        """Increment usage counter for a specific limit type"""
        field_mapping = {
            "listings_per_month": "listings_used",
            "connections_per_month": "connections_used",
            "exports_per_month": "exports_used",
            "api_calls_per_day": "api_calls_used"
        }
        
        field_name = field_mapping.get(limit_type, limit_type.replace("_per_month", "_used").replace("_per_day", "_used"))
        
        self.usage_collection.update_one(
            {
                "user_id": user_id,
                "period_start": {"$lte": datetime.utcnow()},
                "period_end": {"$gte": datetime.utcnow()}
            },
            {"$inc": {field_name: increment}},
            upsert=True
        )

# Export subscription plans for frontend use
def get_subscription_plans():
    """Get all available subscription plans"""
    return SUBSCRIPTION_PLANS

# Export for use in other modules
__all__ = [
    'SubscriptionManager',
    'SubscriptionPlan',
    'SubscriptionStatus',
    'BillingCycle',
    'SubscriptionCreate',
    'SubscriptionUpdate',
    'SubscriptionResponse',
    'UsageStats',
    'FeatureAccess',
    'SUBSCRIPTION_PLANS',
    'get_subscription_plans'
]