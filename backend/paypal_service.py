import paypalrestsdk
import os
from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Optional, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

# PayPal configuration
paypalrestsdk.configure({
    "mode": os.environ.get('PAYPAL_MODE', 'sandbox'),
    "client_id": os.environ.get('PAYPAL_CLIENT_ID'),
    "client_secret": os.environ.get('PAYPAL_SECRET')
})

# Subscription and payment configurations
SUBSCRIPTION_PLANS = {
    "premium_basic": {
        "amount": "10.00",
        "name": "Premium Basic",
        "description": "Access to premium features and enhanced listings"
    },
    "premium_advanced": {
        "amount": "25.00",
        "name": "Premium Advanced", 
        "description": "Advanced analytics, priority support, and unlimited featured listings"
    },
    "enterprise": {
        "amount": "45.00",
        "name": "Enterprise",
        "description": "Full platform access, API integration, and dedicated support"
    }
}

FEATURED_LISTING_PRICES = {
    "standard": {"amount": "5.00", "name": "Standard Featured Listing"},
    "premium": {"amount": "10.00", "name": "Premium Featured Listing"}
}

class PayPalService:
    
    @staticmethod
    async def create_subscription_plan(tier: str) -> Optional[str]:
        """Create a PayPal billing plan for subscription"""
        try:
            if tier not in SUBSCRIPTION_PLANS:
                raise ValueError(f"Invalid subscription tier: {tier}")
            
            plan_data = SUBSCRIPTION_PLANS[tier]
            
            billing_plan = paypalrestsdk.BillingPlan({
                "name": plan_data["name"],
                "description": plan_data["description"],
                "type": "INFINITE",
                "payment_definitions": [{
                    "name": "Regular payment",
                    "type": "REGULAR",
                    "frequency": "MONTH",
                    "frequency_interval": "1",
                    "cycles": "0",
                    "amount": {
                        "currency": "USD",
                        "value": plan_data["amount"]
                    }
                }],
                "merchant_preferences": {
                    "setup_fee": {
                        "currency": "USD",
                        "value": "0"
                    },
                    "return_url": "https://oil-trade-hub.emergent.host/subscription/success",
                    "cancel_url": "https://oil-trade-hub.emergent.host/subscription/cancel",
                    "auto_bill_amount": "YES",
                    "initial_fail_amount_action": "CONTINUE",
                    "max_fail_attempts": "3"
                }
            })
            
            if billing_plan.create():
                # Activate the plan
                if billing_plan.activate():
                    logger.info(f"Created and activated billing plan: {billing_plan.id} for tier: {tier}")
                    return billing_plan.id
                else:
                    logger.error(f"Failed to activate billing plan for tier: {tier}")
            else:
                logger.error(f"Failed to create billing plan for tier: {tier}")
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating subscription plan: {str(e)}")
            return None

    @staticmethod
    async def create_subscription(plan_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal billing agreement for subscription"""
        try:
            billing_agreement = paypalrestsdk.BillingAgreement({
                "name": "Oil & Gas Finder Monthly Subscription",
                "description": "Monthly subscription to Oil & Gas Finder premium features",
                "start_date": (datetime.utcnow() + timedelta(seconds=10)).isoformat() + "Z",
                "plan": {
                    "id": plan_id
                },
                "payer": {
                    "payment_method": "paypal"
                }
            })
            
            if billing_agreement.create():
                # Store in database
                payment_record = {
                    "payment_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "payment_type": "subscription",
                    "status": "pending",
                    "paypal_agreement_id": billing_agreement.id,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                db.payments.insert_one(payment_record)
                
                # Get approval URL
                for link in billing_agreement.links:
                    if link.method == "REDIRECT":
                        logger.info(f"Created subscription agreement: {billing_agreement.id} for user: {user_id}")
                        return {
                            "approval_url": link.href,
                            "agreement_id": billing_agreement.id,
                            "payment_id": payment_record["payment_id"]
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return None

    @staticmethod
    async def create_payment(listing_type: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal payment for featured listing"""
        try:
            if listing_type not in FEATURED_LISTING_PRICES:
                raise ValueError(f"Invalid listing type: {listing_type}")
                
            listing_data = FEATURED_LISTING_PRICES[listing_type]
            
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": "https://oil-trade-hub.emergent.host/payment/success",
                    "cancel_url": "https://oil-trade-hub.emergent.host/payment/cancel"
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": listing_data["name"],
                            "sku": listing_type,
                            "price": listing_data["amount"],
                            "currency": "USD",
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": listing_data["amount"],
                        "currency": "USD"
                    },
                    "description": f"Payment for {listing_data['name']} on Oil & Gas Finder"
                }]
            })
            
            if payment.create():
                # Store in database
                payment_record = {
                    "payment_id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "payment_type": "featured_listing",
                    "amount": float(listing_data["amount"]),
                    "currency": "USD",
                    "status": "pending",
                    "paypal_payment_id": payment.id,
                    "listing_type": listing_type,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                db.payments.insert_one(payment_record)
                
                # Get approval URL
                for link in payment.links:
                    if link.method == "REDIRECT":
                        logger.info(f"Created payment: {payment.id} for user: {user_id}")
                        return {
                            "approval_url": link.href,
                            "payment_id": payment.id,
                            "internal_payment_id": payment_record["payment_id"]
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return None

    @staticmethod
    async def execute_payment(payment_id: str, payer_id: str) -> bool:
        """Execute PayPal payment after user approval"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                # Update database
                result = db.payments.update_one(
                    {"paypal_payment_id": payment_id},
                    {
                        "$set": {
                            "status": "completed",
                            "updated_at": datetime.utcnow(),
                            "payer_id": payer_id
                        }
                    }
                )
                
                if result.modified_count > 0:
                    logger.info(f"Payment executed successfully: {payment_id}")
                    return True
                else:
                    logger.error(f"Failed to update payment record for: {payment_id}")
                    
            return False
            
        except Exception as e:
            logger.error(f"Error executing payment: {str(e)}")
            return False

    @staticmethod
    async def execute_agreement(agreement_token: str) -> bool:
        """Execute PayPal billing agreement after user approval"""
        try:
            billing_agreement = paypalrestsdk.BillingAgreement.execute(agreement_token)
            
            if billing_agreement:
                # Update database
                result = db.payments.update_one(
                    {"paypal_agreement_id": agreement_token},
                    {
                        "$set": {
                            "status": "active",
                            "updated_at": datetime.utcnow(),
                            "agreement_id": billing_agreement.id
                        }
                    }
                )
                
                # Update user subscription status
                payment_record = db.payments.find_one({"paypal_agreement_id": agreement_token})
                if payment_record:
                    db.users.update_one(
                        {"user_id": payment_record["user_id"]},
                        {
                            "$set": {
                                "role": "premium",
                                "subscription_status": "active",
                                "subscription_start": datetime.utcnow()
                            }
                        }
                    )
                
                if result.modified_count > 0:
                    logger.info(f"Agreement executed successfully: {agreement_token}")
                    return True
                else:
                    logger.error(f"Failed to update agreement record for: {agreement_token}")
                    
            return False
            
        except Exception as e:
            logger.error(f"Error executing agreement: {str(e)}")
            return False

    @staticmethod
    async def get_payment_status(payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment status from database"""
        try:
            payment_record = db.payments.find_one(
                {"$or": [
                    {"payment_id": payment_id},
                    {"paypal_payment_id": payment_id},
                    {"paypal_agreement_id": payment_id}
                ]},
                {"_id": 0}
            )
            
            if payment_record:
                return {
                    "payment_id": payment_record.get("payment_id"),
                    "status": payment_record.get("status"),
                    "amount": payment_record.get("amount"),
                    "payment_type": payment_record.get("payment_type"),
                    "created_at": payment_record.get("created_at"),
                    "updated_at": payment_record.get("updated_at")
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None

    @staticmethod
    async def cancel_subscription(agreement_id: str, user_id: str) -> bool:
        """Cancel PayPal subscription"""
        try:
            billing_agreement = paypalrestsdk.BillingAgreement.find(agreement_id)
            
            if billing_agreement.cancel({"note": "User requested cancellation"}):
                # Update database
                db.payments.update_one(
                    {"agreement_id": agreement_id, "user_id": user_id},
                    {
                        "$set": {
                            "status": "cancelled",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update user subscription status
                db.users.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "role": "basic",
                            "subscription_status": "cancelled",
                            "subscription_end": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Subscription cancelled: {agreement_id} for user: {user_id}")
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return False

    @staticmethod
    async def get_user_payments(user_id: str) -> List[Dict[str, Any]]:
        """Get all payments for a user"""
        try:
            payments = list(
                db.payments.find(
                    {"user_id": user_id},
                    {"_id": 0}
                ).sort("created_at", -1)
            )
            
            return payments
            
        except Exception as e:
            logger.error(f"Error getting user payments: {str(e)}")
            return []
