from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
import uuid
import logging
from email_service import email_service

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class BusinessGrowthService:
    """Business growth and user acquisition service for Oil & Gas Finder platform"""

    @staticmethod
    async def create_referral_program(user_id: str, referral_type: str = "standard") -> Dict[str, Any]:
        """Create referral program for user acquisition"""
        try:
            referral_code = f"OGF{str(uuid.uuid4())[:8].upper()}"
            
            referral_rewards = {
                "standard": {
                    "referrer_reward": 25.00,  # $25 credit for referrer
                    "referee_reward": 15.00,   # $15 discount for new user
                    "subscription_bonus": 10.00  # Additional bonus if referee subscribes
                },
                "premium": {
                    "referrer_reward": 50.00,
                    "referee_reward": 25.00,
                    "subscription_bonus": 25.00
                },
                "enterprise": {
                    "referrer_reward": 100.00,
                    "referee_reward": 50.00,
                    "subscription_bonus": 50.00
                }
            }
            
            reward_structure = referral_rewards.get(referral_type, referral_rewards["standard"])
            
            referral_program = {
                "referral_id": str(uuid.uuid4()),
                "user_id": user_id,
                "referral_code": referral_code,
                "referral_type": referral_type,
                "reward_structure": reward_structure,
                "total_referrals": 0,
                "successful_conversions": 0,
                "total_rewards_earned": 0.0,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            db.referral_programs.insert_one(referral_program)
            
            logger.info(f"Created referral program for user {user_id} with code {referral_code}")
            return {
                "referral_code": referral_code,
                "referral_id": referral_program["referral_id"],
                "reward_structure": reward_structure
            }
            
        except Exception as e:
            logger.error(f"Error creating referral program: {str(e)}")
            return {}

    @staticmethod
    async def process_referral_signup(referral_code: str, new_user_id: str) -> Dict[str, Any]:
        """Process new user signup through referral"""
        try:
            # Find referral program
            referral_program = db.referral_programs.find_one({"referral_code": referral_code, "status": "active"})
            if not referral_program:
                return {"success": False, "message": "Invalid referral code"}
            
            referrer_user = db.users.find_one({"user_id": referral_program["user_id"]})
            new_user = db.users.find_one({"user_id": new_user_id})
            
            if not referrer_user or not new_user:
                return {"success": False, "message": "User not found"}
            
            # Create referral record
            referral_record = {
                "referral_record_id": str(uuid.uuid4()),
                "referral_program_id": referral_program["referral_id"],
                "referrer_user_id": referral_program["user_id"],
                "referee_user_id": new_user_id,
                "referral_code": referral_code,
                "signup_date": datetime.utcnow(),
                "conversion_date": None,
                "status": "pending",  # pending, converted, rewarded
                "referrer_reward": 0.0,
                "referee_discount": referral_program["reward_structure"]["referee_reward"],
                "created_at": datetime.utcnow()
            }
            
            db.referral_records.insert_one(referral_record)
            
            # Update referral program stats
            db.referral_programs.update_one(
                {"referral_id": referral_program["referral_id"]},
                {
                    "$inc": {"total_referrals": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Give referee discount/credit
            user_credit = {
                "user_id": new_user_id,
                "credit_amount": referral_program["reward_structure"]["referee_discount"],
                "credit_type": "referral_signup",
                "referral_code": referral_code,
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            db.user_credits.insert_one(user_credit)
            
            # Send notification emails
            if email_service:
                # Email to referee (new user)
                await email_service.send_referral_welcome_email(
                    new_user["email"],
                    new_user["first_name"],
                    referral_program["reward_structure"]["referee_reward"],
                    referrer_user["company_name"]
                )
                
                # Email to referrer
                await email_service.send_referral_notification_email(
                    referrer_user["email"],
                    referrer_user["first_name"],
                    new_user["first_name"],
                    new_user["company_name"]
                )
            
            logger.info(f"Processed referral signup: {referral_code} -> {new_user_id}")
            return {
                "success": True,
                "referee_discount": referral_program["reward_structure"]["referee_discount"],
                "referrer_company": referrer_user["company_name"]
            }
            
        except Exception as e:
            logger.error(f"Error processing referral signup: {str(e)}")
            return {"success": False, "message": "Error processing referral"}

    @staticmethod
    async def process_referral_conversion(referee_user_id: str, conversion_type: str = "subscription") -> bool:
        """Process referral conversion when referee makes a purchase"""
        try:
            # Find pending referral record
            referral_record = db.referral_records.find_one({
                "referee_user_id": referee_user_id,
                "status": "pending"
            })
            
            if not referral_record:
                return False
            
            referral_program = db.referral_programs.find_one({
                "referral_id": referral_record["referral_program_id"]
            })
            
            if not referral_program:
                return False
            
            # Calculate rewards
            base_reward = referral_program["reward_structure"]["referrer_reward"]
            bonus_reward = 0
            
            if conversion_type == "subscription":
                bonus_reward = referral_program["reward_structure"]["subscription_bonus"]
            
            total_reward = base_reward + bonus_reward
            
            # Update referral record
            db.referral_records.update_one(
                {"referral_record_id": referral_record["referral_record_id"]},
                {
                    "$set": {
                        "status": "converted",
                        "conversion_date": datetime.utcnow(),
                        "conversion_type": conversion_type,
                        "referrer_reward": total_reward
                    }
                }
            )
            
            # Update referral program stats
            db.referral_programs.update_one(
                {"referral_id": referral_program["referral_id"]},
                {
                    "$inc": {
                        "successful_conversions": 1,
                        "total_rewards_earned": total_reward
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Give referrer reward
            referrer_credit = {
                "user_id": referral_record["referrer_user_id"],
                "credit_amount": total_reward,
                "credit_type": f"referral_{conversion_type}",
                "referral_record_id": referral_record["referral_record_id"],
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            db.user_credits.insert_one(referrer_credit)
            
            # Send reward notification
            if email_service:
                referrer_user = db.users.find_one({"user_id": referral_record["referrer_user_id"]})
                referee_user = db.users.find_one({"user_id": referee_user_id})
                
                if referrer_user and referee_user:
                    await email_service.send_referral_reward_email(
                        referrer_user["email"],
                        referrer_user["first_name"],
                        total_reward,
                        referee_user["company_name"],
                        conversion_type
                    )
            
            logger.info(f"Processed referral conversion: {referee_user_id} -> ${total_reward} reward")
            return True
            
        except Exception as e:
            logger.error(f"Error processing referral conversion: {str(e)}")
            return False

    @staticmethod
    async def create_lead_magnet(title: str, content_type: str, target_audience: str) -> Dict[str, Any]:
        """Create lead magnets for user acquisition"""
        try:
            lead_magnets = {
                "oil_price_report": {
                    "title": "2024 Oil Price Forecast Report",
                    "description": "Comprehensive analysis of global oil price trends and predictions",
                    "content_type": "PDF Report",
                    "value_proposition": "Exclusive market insights from industry experts",
                    "download_url": "/downloads/oil-price-forecast-2024.pdf"
                },
                "gas_trading_guide": {
                    "title": "Complete Guide to Natural Gas Trading",
                    "description": "Step-by-step guide to successful gas trading strategies",
                    "content_type": "eBook",
                    "value_proposition": "Learn from experienced gas traders",
                    "download_url": "/downloads/gas-trading-guide.pdf"
                },
                "market_intelligence": {
                    "title": "Weekly Market Intelligence Brief",
                    "description": "Weekly updates on oil & gas market movements",
                    "content_type": "Email Newsletter",
                    "value_proposition": "Stay ahead with weekly market insights",
                    "signup_url": "/newsletter/market-intelligence"
                },
                "trading_calculator": {
                    "title": "Oil & Gas Profit Calculator",
                    "description": "Calculate potential profits from oil and gas trades",
                    "content_type": "Interactive Tool",
                    "value_proposition": "Free tool to optimize your trading profits",
                    "tool_url": "/tools/profit-calculator"
                }
            }
            
            lead_magnet = lead_magnets.get(content_type, {
                "title": title,
                "description": f"Valuable {content_type} for {target_audience}",
                "content_type": content_type,
                "value_proposition": "Exclusive industry insights",
                "download_url": f"/downloads/{title.lower().replace(' ', '-')}.pdf"
            })
            
            lead_magnet_record = {
                "lead_magnet_id": str(uuid.uuid4()),
                "title": lead_magnet["title"],
                "description": lead_magnet["description"],
                "content_type": lead_magnet["content_type"],
                "target_audience": target_audience,
                "value_proposition": lead_magnet["value_proposition"],
                "download_url": lead_magnet.get("download_url"),
                "signup_url": lead_magnet.get("signup_url"),
                "tool_url": lead_magnet.get("tool_url"),
                "downloads": 0,
                "leads_generated": 0,
                "conversion_rate": 0.0,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            db.lead_magnets.insert_one(lead_magnet_record)
            
            return lead_magnet_record
            
        except Exception as e:
            logger.error(f"Error creating lead magnet: {str(e)}")
            return {}

    @staticmethod
    async def track_lead_generation(lead_magnet_id: str, user_email: str, source: str = "organic") -> bool:
        """Track lead generation from lead magnets"""
        try:
            lead_record = {
                "lead_id": str(uuid.uuid4()),
                "lead_magnet_id": lead_magnet_id,
                "email": user_email,
                "source": source,  # organic, social, paid, referral
                "status": "new",  # new, contacted, qualified, converted
                "created_at": datetime.utcnow()
            }
            
            db.leads.insert_one(lead_record)
            
            # Update lead magnet stats
            db.lead_magnets.update_one(
                {"lead_magnet_id": lead_magnet_id},
                {"$inc": {"leads_generated": 1}}
            )
            
            # Send lead magnet content
            if email_service:
                lead_magnet = db.lead_magnets.find_one({"lead_magnet_id": lead_magnet_id})
                if lead_magnet:
                    await email_service.send_lead_magnet_email(
                        user_email,
                        lead_magnet["title"],
                        lead_magnet["description"],
                        lead_magnet.get("download_url", "")
                    )
            
            logger.info(f"Tracked lead generation: {user_email} from {lead_magnet_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking lead generation: {str(e)}")
            return False

    @staticmethod
    async def create_partnership_program(partner_type: str, commission_rate: float) -> Dict[str, Any]:
        """Create partnership and affiliate programs"""
        try:
            partnership_programs = {
                "affiliate": {
                    "name": "Oil & Gas Finder Affiliate Program",
                    "description": "Earn commissions by referring trading professionals",
                    "commission_structure": {
                        "signup_commission": 25.00,
                        "subscription_commission_rate": 0.20,  # 20% of first payment
                        "recurring_commission_rate": 0.10      # 10% of recurring payments
                    },
                    "requirements": {
                        "min_monthly_referrals": 5,
                        "quality_score_min": 4.0
                    }
                },
                "strategic": {
                    "name": "Strategic Partnership Program",
                    "description": "Revenue sharing for industry partners",
                    "commission_structure": {
                        "revenue_share_rate": 0.30,
                        "co_marketing_bonus": 500.00,
                        "exclusive_territory_bonus": 1000.00
                    },
                    "requirements": {
                        "min_monthly_revenue": 10000.00,
                        "exclusive_territory": True
                    }
                },
                "reseller": {
                    "name": "Authorized Reseller Program",
                    "description": "White-label solutions for industry consultants",
                    "commission_structure": {
                        "markup_percentage": 0.40,
                        "implementation_fee": 2500.00,
                        "training_bonus": 1000.00
                    },
                    "requirements": {
                        "certification_required": True,
                        "min_client_commitment": 10
                    }
                }
            }
            
            program_config = partnership_programs.get(partner_type, partnership_programs["affiliate"])
            
            partnership_program = {
                "program_id": str(uuid.uuid4()),
                "partner_type": partner_type,
                "name": program_config["name"],
                "description": program_config["description"],
                "commission_rate": commission_rate,
                "commission_structure": program_config["commission_structure"],
                "requirements": program_config["requirements"],
                "total_partners": 0,
                "total_revenue_generated": 0.0,
                "total_commissions_paid": 0.0,
                "status": "active",
                "created_at": datetime.utcnow()
            }
            
            db.partnership_programs.insert_one(partnership_program)
            
            return partnership_program
            
        except Exception as e:
            logger.error(f"Error creating partnership program: {str(e)}")
            return {}

    @staticmethod
    async def calculate_conversion_metrics() -> Dict[str, Any]:
        """Calculate user acquisition and conversion metrics"""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            
            # Lead conversion metrics
            total_leads = db.leads.count_documents({})
            converted_leads = db.leads.count_documents({"status": "converted"})
            lead_conversion_rate = (converted_leads / max(total_leads, 1)) * 100
            
            # Referral metrics
            total_referrals = db.referral_records.count_documents({})
            converted_referrals = db.referral_records.count_documents({"status": "converted"})
            referral_conversion_rate = (converted_referrals / max(total_referrals, 1)) * 100
            
            # User acquisition cost (mock calculation)
            marketing_spend = 5000.00  # Monthly marketing budget
            new_users_30d = db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
            customer_acquisition_cost = marketing_spend / max(new_users_30d, 1)
            
            # Customer lifetime value
            avg_subscription_value = 25.00  # Average monthly subscription
            avg_customer_lifetime = 12  # months
            customer_lifetime_value = avg_subscription_value * avg_customer_lifetime
            
            # ROI calculation
            ltv_cac_ratio = customer_lifetime_value / max(customer_acquisition_cost, 1)
            
            return {
                "lead_metrics": {
                    "total_leads": total_leads,
                    "converted_leads": converted_leads,
                    "conversion_rate": round(lead_conversion_rate, 2)
                },
                "referral_metrics": {
                    "total_referrals": total_referrals,
                    "converted_referrals": converted_referrals,
                    "conversion_rate": round(referral_conversion_rate, 2)
                },
                "acquisition_metrics": {
                    "customer_acquisition_cost": round(customer_acquisition_cost, 2),
                    "customer_lifetime_value": round(customer_lifetime_value, 2),
                    "ltv_cac_ratio": round(ltv_cac_ratio, 2),
                    "new_users_30d": new_users_30d
                },
                "roi_analysis": {
                    "marketing_efficiency": "Excellent" if ltv_cac_ratio > 3 else "Good" if ltv_cac_ratio > 2 else "Needs Improvement",
                    "payback_period_months": round(customer_acquisition_cost / avg_subscription_value, 1),
                    "projected_monthly_growth": f"{round((new_users_30d * 1.1) - new_users_30d, 0)} users"
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating conversion metrics: {str(e)}")
            return {}

    @staticmethod
    async def get_user_acquisition_dashboard() -> Dict[str, Any]:
        """Get comprehensive user acquisition dashboard"""
        try:
            now = datetime.utcnow()
            seven_days_ago = now - timedelta(days=7)
            thirty_days_ago = now - timedelta(days=30)
            
            # Traffic sources analysis
            traffic_sources = list(db.leads.aggregate([
                {"$group": {
                    "_id": "$source",
                    "leads": {"$sum": 1},
                    "conversions": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "converted"]}, 1, 0]
                        }
                    }
                }},
                {"$sort": {"leads": -1}}
            ]))
            
            # Referral program performance
            top_referrers = list(db.referral_programs.aggregate([
                {"$sort": {"total_rewards_earned": -1}},
                {"$limit": 10},
                {"$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_info"
                }},
                {"$project": {
                    "referral_code": 1,
                    "total_referrals": 1,
                    "successful_conversions": 1,
                    "total_rewards_earned": 1,
                    "company_name": {"$arrayElemAt": ["$user_info.company_name", 0]}
                }}
            ]))
            
            # Lead magnet performance
            lead_magnet_stats = list(db.lead_magnets.aggregate([
                {"$sort": {"leads_generated": -1}},
                {"$project": {
                    "title": 1,
                    "content_type": 1,
                    "leads_generated": 1,
                    "downloads": 1,
                    "conversion_rate": {
                        "$multiply": [
                            {"$divide": ["$leads_generated", {"$max": ["$downloads", 1]}]},
                            100
                        ]
                    }
                }}
            ]))
            
            # Growth projections
            recent_growth = db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
            monthly_projection = recent_growth * 4.3  # Weekly to monthly projection
            
            return {
                "traffic_sources": traffic_sources,
                "top_referrers": top_referrers,
                "lead_magnet_performance": lead_magnet_stats,
                "growth_projections": {
                    "weekly_signups": recent_growth,
                    "projected_monthly": int(monthly_projection),
                    "growth_trend": "Increasing" if recent_growth > 10 else "Stable"
                },
                "conversion_funnel": {
                    "website_visitors": 5000,  # Mock data - would integrate with analytics
                    "leads_generated": db.leads.count_documents({"created_at": {"$gte": thirty_days_ago}}),
                    "trial_signups": db.users.count_documents({"created_at": {"$gte": thirty_days_ago}}),
                    "paid_conversions": db.payments.count_documents({
                        "status": "completed",
                        "created_at": {"$gte": thirty_days_ago}
                    })
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user acquisition dashboard: {str(e)}")
            return {}

# Create global business growth service instance
business_growth_service = BusinessGrowthService()
