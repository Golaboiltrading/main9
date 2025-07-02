import paypalrestsdk
import os
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient # MODIFIED
from typing import Optional, Dict, Any, List
import uuid
import logging
from fastapi.concurrency import run_in_threadpool # MODIFIED
# import asyncio # Not strictly needed if only using run_in_threadpool

logger = logging.getLogger(__name__)

# MongoDB connection:
# This service should ideally use the 'db' object initialized in server.py's startup event.
# For now, to make it runnable standalone for refactoring and to ensure 'db' is async,
# we'll define a way to get an async db client.
# In a real integration, 'db' would be passed from server.py or accessed via a shared module.

_db_client = None
_db_oil_gas_finder = None

async def _get_db():
    global _db_client, _db_oil_gas_finder
    if _db_oil_gas_finder is None:
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        _db_client = AsyncIOMotorClient(mongo_url)
        _db_oil_gas_finder = _db_client.oil_gas_finder # Use the database name from original code
    return _db_oil_gas_finder

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
            
            # Synchronous SDK call, needs to be wrapped
            def _create_paypal_billing_plan_sync():
                return paypalrestsdk.BillingPlan({
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

            billing_plan = await run_in_threadpool(_create_paypal_billing_plan_sync)

            # Synchronous SDK calls for create and activate
            def _create_and_activate_plan_sync(plan_obj):
                if plan_obj.create():
                    if plan_obj.activate():
                        return plan_obj.id
                logger.error(f"PayPal SDK error during plan creation/activation: {plan_obj.error if hasattr(plan_obj, 'error') else 'Unknown SDK error'}")
                return None

            plan_id = await run_in_threadpool(_create_and_activate_plan_sync, billing_plan)
            
            if plan_id:
                logger.info(f"Created and activated billing plan: {plan_id} for tier: {tier}")
                return plan_id
            # Error logging is now inside _create_and_activate_plan_sync if it fails
            return None
            
        except Exception as e:
            logger.error(f"Error creating subscription plan: {str(e)}")
            return None

    @staticmethod
    async def create_subscription(plan_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal billing agreement for subscription"""
        db_conn = await _get_db()
        try:
            def _create_paypal_billing_agreement_sync():
                return paypalrestsdk.BillingAgreement({
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
            
            billing_agreement = await run_in_threadpool(_create_paypal_billing_agreement_sync)

            def _billing_agreement_create_sync(agreement_obj):
                if agreement_obj.create():
                    return True
                logger.error(f"PayPal SDK error during agreement creation: {agreement_obj.error if hasattr(agreement_obj, 'error') else 'Unknown SDK error'}")
                return False

            if await run_in_threadpool(_billing_agreement_create_sync, billing_agreement):
                # Store in database
                payment_record = {
                    "payment_id": str(uuid.uuid4()), # This is internal payment_id
                    "user_id": user_id,
                    "payment_type": "subscription",
                    "status": "pending",
                    "paypal_agreement_id": billing_agreement.id, # PayPal's agreement ID
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await db_conn.payments.insert_one(payment_record)
                
                # Get approval URL
                for link in billing_agreement.links: # Links are available on the original object
                    if link.method == "REDIRECT":
                        logger.info(f"Created subscription agreement: {billing_agreement.id} for user: {user_id}")
                        return {
                            "approval_url": link.href,
                            "agreement_id": billing_agreement.id, # PayPal's agreement ID
                            "payment_id": payment_record["payment_id"] # Internal payment_id
                        }
            return None
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            return None

    @staticmethod
    async def create_payment(listing_type: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Create a PayPal payment for featured listing"""
        try:
            db_conn = await _get_db()
            if listing_type not in FEATURED_LISTING_PRICES:
                raise ValueError(f"Invalid listing type: {listing_type}")
                
            listing_data = FEATURED_LISTING_PRICES[listing_type]

            def _create_paypal_payment_sync():
                return paypalrestsdk.Payment({
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

            payment = await run_in_threadpool(_create_paypal_payment_sync)

            def _payment_create_sync(p_obj):
                if p_obj.create():
                    return True
                logger.error(f"PayPal SDK error during payment creation: {p_obj.error if hasattr(p_obj, 'error') else 'Unknown SDK error'}")
                return False

            if await run_in_threadpool(_payment_create_sync, payment):
                # Store in database
                payment_record = {
                    "payment_id": str(uuid.uuid4()), # Internal payment_id
                    "user_id": user_id,
                    "payment_type": "featured_listing",
                    "amount": float(listing_data["amount"]),
                    "currency": "USD",
                    "status": "pending",
                    "paypal_payment_id": payment.id, # PayPal's payment ID
                    "listing_type": listing_type,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
                
                await db_conn.payments.insert_one(payment_record)
                
                # Get approval URL
                for link in payment.links:
                    if link.method == "REDIRECT":
                        logger.info(f"Created payment: {payment.id} for user: {user_id}")
                        return {
                            "approval_url": link.href,
                            "payment_id": payment.id, # PayPal's payment ID
                            "internal_payment_id": payment_record["payment_id"] # Internal payment_id
                        }
            return None
            
        except Exception as e:
            logger.error(f"Error creating payment: {str(e)}")
            return None

    @staticmethod
    async def execute_payment(payment_id: str, payer_id: str) -> bool:
        """Execute PayPal payment after user approval"""
        db_conn = await _get_db()
        try:
            def _find_and_execute_payment_sync():
                payment_obj = paypalrestsdk.Payment.find(payment_id)
                if payment_obj.execute({"payer_id": payer_id}):
                    return True, None # Success, no error
                return False, payment_obj.error if hasattr(payment_obj, 'error') else "Unknown SDK error during execute"
            
            success, error_detail = await run_in_threadpool(_find_and_execute_payment_sync)

            if success:
                # Update database
                result = await db_conn.payments.update_one(
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
                    logger.error(f"Failed to update payment record for: {payment_id}, though PayPal execution was successful.")
                    # Consider how to handle this discrepancy. For now, return based on DB update.
                    return False
            else:
                logger.error(f"PayPal payment execution failed: {payment_id}. Error: {error_detail}")
                return False
            
        except Exception as e:
            logger.error(f"Error executing payment: {str(e)}")
            return False

    @staticmethod
    async def execute_agreement(agreement_token: str) -> bool:
        """Execute PayPal billing agreement after user approval"""
        db_conn = await _get_db()
        try:
            def _execute_billing_agreement_sync():
                # agreement_token here is the one from the redirect, often called 'token' by PayPal
                agreement_obj = paypalrestsdk.BillingAgreement.execute(agreement_token)
                # The execute method for agreements might not return a boolean directly,
                # but rather the executed agreement object or raise an error.
                # We assume it's truthy on success here.
                if agreement_obj : # Check if it's a valid object, not False or None
                     return agreement_obj, None
                return None, "PayPal SDK BillingAgreement.execute failed" # Or parse error from agreement_obj.error

            billing_agreement, error_detail = await run_in_threadpool(_execute_billing_agreement_sync)

            if billing_agreement and hasattr(billing_agreement, 'id'):
                # Update database
                result = await db_conn.payments.update_one(
                    {"paypal_agreement_id": billing_agreement.id}, # Match on the actual agreement ID post-execution
                    {
                        "$set": {
                            "status": "active",
                            "updated_at": datetime.utcnow(),
                            "agreement_id": billing_agreement.id # Storing the final agreement ID
                        }
                    }
                )
                
                # Update user subscription status
                # It's better to find the payment record using the original token/ID used to initiate
                # as billing_agreement.id might be newly generated or confirmed at this stage.
                # Assuming paypal_agreement_id was stored as the initial token/id for lookup.
                payment_record = await db_conn.payments.find_one({"paypal_agreement_id": agreement_token})
                if payment_record:
                    await db_conn.users.update_one(
                        {"user_id": payment_record["user_id"]},
                        {
                            "$set": {
                                "role": "premium", # This should be dynamic based on the plan
                                "subscription_status": "active",
                                "subscription_start": datetime.utcnow()
                            }
                        }
                    )
                
                if result.modified_count > 0:
                    logger.info(f"Agreement executed successfully: {billing_agreement.id}")
                    return True
                else:
                    logger.error(f"Failed to update agreement record for: {billing_agreement.id}, though PayPal execution may have succeeded.")
                    return False
            else:
                logger.error(f"PayPal agreement execution failed for token: {agreement_token}. Error: {error_detail}")
                return False
            
        except Exception as e:
            logger.error(f"Error executing agreement: {str(e)}")
            return False

    @staticmethod
    async def get_payment_status(payment_id: str) -> Optional[Dict[str, Any]]: # payment_id is internal
        """Get payment status from database"""
        db_conn = await _get_db()
        try:
            payment_record = await db_conn.payments.find_one(
                # Search by internal payment_id, or paypal_payment_id, or paypal_agreement_id
                {"$or": [
                    {"payment_id": payment_id},
                    {"paypal_payment_id": payment_id},
                    {"paypal_agreement_id": payment_id}
                ]},
                {"_id": 0}
            )
            
            if payment_record:
                return {
                    "payment_id": payment_record.get("payment_id"), # Return internal ID
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
        db_conn = await _get_db()
        try:
            def _find_and_cancel_agreement_sync():
                agreement_obj = paypalrestsdk.BillingAgreement.find(agreement_id)
                # The 'cancel' method on the SDK object might return a boolean or the object itself.
                # Assuming it's truthy on success.
                if agreement_obj.cancel({"note": "User requested cancellation"}):
                    return True, None
                return False, agreement_obj.error if hasattr(agreement_obj, 'error') else "Unknown SDK error during cancel"

            success, error_detail = await run_in_threadpool(_find_and_cancel_agreement_sync)

            if success:
                # Update database
                await db_conn.payments.update_one(
                    {"agreement_id": agreement_id, "user_id": user_id}, # Match by PayPal's agreement ID
                    {
                        "$set": {
                            "status": "cancelled",
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update user subscription status
                await db_conn.users.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "role": "basic", # Revert to basic or based on logic
                            "subscription_status": "cancelled",
                            "subscription_end": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Subscription cancelled: {agreement_id} for user: {user_id}")
                return True
            else:
                logger.error(f"PayPal subscription cancellation failed for {agreement_id}. Error: {error_detail}")
                return False
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            return False

    @staticmethod
    async def get_user_payments(user_id: str) -> List[Dict[str, Any]]:
        """Get all payments for a user"""
        db_conn = await _get_db()
        try:
            cursor = db_conn.payments.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("created_at", -1)
            payments = await cursor.to_list(length=None)
            
            return payments
            
        except Exception as e:
            logger.error(f"Error getting user payments: {str(e)}")
            return []
