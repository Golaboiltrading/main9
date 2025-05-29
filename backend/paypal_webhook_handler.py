from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class PayPalWebhookHandler:
    """Handle PayPal webhook notifications for payment confirmations"""
    
    @staticmethod
    async def handle_webhook(request: Request):
        """Process PayPal webhook notifications"""
        try:
            # Get webhook data
            webhook_data = await request.json()
            event_type = webhook_data.get('event_type')
            resource = webhook_data.get('resource', {})
            
            logger.info(f"PayPal webhook received: {event_type}")
            
            # Handle different webhook events
            if event_type == 'PAYMENT.SALE.COMPLETED':
                await PayPalWebhookHandler._handle_payment_completed(resource)
                
            elif event_type == 'BILLING.SUBSCRIPTION.CREATED':
                await PayPalWebhookHandler._handle_subscription_created(resource)
                
            elif event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
                await PayPalWebhookHandler._handle_subscription_activated(resource)
                
            elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
                await PayPalWebhookHandler._handle_subscription_cancelled(resource)
                
            elif event_type == 'BILLING.SUBSCRIPTION.PAYMENT.COMPLETED':
                await PayPalWebhookHandler._handle_subscription_payment(resource)
                
            # Store webhook for audit trail
            webhook_record = {
                "webhook_id": webhook_data.get('id'),
                "event_type": event_type,
                "resource": resource,
                "processed_at": datetime.utcnow(),
                "status": "processed"
            }
            
            db.paypal_webhooks.insert_one(webhook_record)
            
            return {"status": "success", "message": "Webhook processed"}
            
        except Exception as e:
            logger.error(f"Error processing PayPal webhook: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    @staticmethod
    async def _handle_payment_completed(resource):
        """Handle completed one-time payments (featured listings)"""
        try:
            payment_id = resource.get('parent_payment')
            amount = float(resource.get('amount', {}).get('total', 0))
            
            # Update payment record
            db.payments.update_one(
                {"paypal_payment_id": payment_id},
                {
                    "$set": {
                        "status": "completed",
                        "amount_received": amount,
                        "completed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Payment completed: {payment_id} - ${amount}")
            
        except Exception as e:
            logger.error(f"Error handling payment completion: {str(e)}")
    
    @staticmethod
    async def _handle_subscription_created(resource):
        """Handle subscription creation"""
        try:
            subscription_id = resource.get('id')
            
            # Update subscription record
            db.payments.update_one(
                {"paypal_agreement_id": subscription_id},
                {
                    "$set": {
                        "status": "created",
                        "subscription_created_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Subscription created: {subscription_id}")
            
        except Exception as e:
            logger.error(f"Error handling subscription creation: {str(e)}")
    
    @staticmethod
    async def _handle_subscription_activated(resource):
        """Handle subscription activation"""
        try:
            subscription_id = resource.get('id')
            
            # Find payment record and get user
            payment_record = db.payments.find_one({"paypal_agreement_id": subscription_id})
            if payment_record:
                user_id = payment_record["user_id"]
                
                # Update payment record
                db.payments.update_one(
                    {"paypal_agreement_id": subscription_id},
                    {
                        "$set": {
                            "status": "active",
                            "activated_at": datetime.utcnow()
                        }
                    }
                )
                
                # Update user role to premium
                db.users.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "role": "premium",
                            "subscription_status": "active",
                            "subscription_activated_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Subscription activated: {subscription_id} for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling subscription activation: {str(e)}")
    
    @staticmethod
    async def _handle_subscription_cancelled(resource):
        """Handle subscription cancellation"""
        try:
            subscription_id = resource.get('id')
            
            # Find payment record and get user
            payment_record = db.payments.find_one({"paypal_agreement_id": subscription_id})
            if payment_record:
                user_id = payment_record["user_id"]
                
                # Update payment record
                db.payments.update_one(
                    {"paypal_agreement_id": subscription_id},
                    {
                        "$set": {
                            "status": "cancelled",
                            "cancelled_at": datetime.utcnow()
                        }
                    }
                )
                
                # Downgrade user to basic
                db.users.update_one(
                    {"user_id": user_id},
                    {
                        "$set": {
                            "role": "basic",
                            "subscription_status": "cancelled",
                            "subscription_cancelled_at": datetime.utcnow()
                        }
                    }
                )
                
                logger.info(f"Subscription cancelled: {subscription_id} for user: {user_id}")
            
        except Exception as e:
            logger.error(f"Error handling subscription cancellation: {str(e)}")
    
    @staticmethod
    async def _handle_subscription_payment(resource):
        """Handle recurring subscription payments"""
        try:
            subscription_id = resource.get('billing_agreement_id')
            amount = float(resource.get('amount', {}).get('total', 0))
            
            # Find payment record and get user
            payment_record = db.payments.find_one({"paypal_agreement_id": subscription_id})
            if payment_record:
                user_id = payment_record["user_id"]
                
                # Create payment record for this billing cycle
                recurring_payment = {
                    "payment_id": resource.get('id'),
                    "user_id": user_id,
                    "payment_type": "subscription_billing",
                    "amount": amount,
                    "subscription_id": subscription_id,
                    "billing_cycle": datetime.utcnow().strftime("%Y-%m"),
                    "status": "completed",
                    "created_at": datetime.utcnow()
                }
                
                db.subscription_payments.insert_one(recurring_payment)
                
                # Update total revenue
                db.payments.update_one(
                    {"paypal_agreement_id": subscription_id},
                    {
                        "$inc": {"total_revenue": amount},
                        "$set": {"last_payment_at": datetime.utcnow()}
                    }
                )
                
                logger.info(f"Subscription payment received: {subscription_id} - ${amount}")
            
        except Exception as e:
            logger.error(f"Error handling subscription payment: {str(e)}")

# Global webhook handler instance
paypal_webhook_handler = PayPalWebhookHandler()