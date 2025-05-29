from datetime import datetime, timedelta
from pymongo import MongoClient
from typing import Dict, List, Any, Optional
import os
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

class AnalyticsService:
    """Advanced analytics and reporting service for Oil & Gas Finder platform"""

    @staticmethod
    async def get_platform_overview() -> Dict[str, Any]:
        """Get comprehensive platform overview analytics"""
        try:
            now = datetime.utcnow()
            thirty_days_ago = now - timedelta(days=30)
            seven_days_ago = now - timedelta(days=7)
            
            # Basic counts
            total_users = db.users.count_documents({})
            total_listings = db.listings.count_documents({})
            total_connections = db.connections.count_documents({})
            
            # Growth metrics
            new_users_30d = db.users.count_documents({"created_at": {"$gte": thirty_days_ago}})
            new_users_7d = db.users.count_documents({"created_at": {"$gte": seven_days_ago}})
            new_listings_30d = db.listings.count_documents({"created_at": {"$gte": thirty_days_ago}})
            new_listings_7d = db.listings.count_documents({"created_at": {"$gte": seven_days_ago}})
            
            # Premium metrics
            premium_users = db.users.count_documents({"role": {"$ne": "basic"}})
            active_subscriptions = db.payments.count_documents({
                "payment_type": "subscription",
                "status": "active"
            })
            
            # Revenue metrics
            revenue_pipeline = list(db.payments.aggregate([
                {"$match": {"status": "completed"}},
                {"$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$amount"},
                    "subscription_revenue": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$payment_type", "subscription"]},
                                "$amount",
                                0
                            ]
                        }
                    },
                    "listing_revenue": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$payment_type", "featured_listing"]},
                                "$amount",
                                0
                            ]
                        }
                    }
                }}
            ]))
            
            revenue_data = revenue_pipeline[0] if revenue_pipeline else {
                "total_revenue": 0,
                "subscription_revenue": 0,
                "listing_revenue": 0
            }
            
            return {
                "overview": {
                    "total_users": total_users,
                    "total_listings": total_listings,
                    "total_connections": total_connections,
                    "premium_users": premium_users,
                    "active_subscriptions": active_subscriptions
                },
                "growth": {
                    "new_users_30d": new_users_30d,
                    "new_users_7d": new_users_7d,
                    "new_listings_30d": new_listings_30d,
                    "new_listings_7d": new_listings_7d,
                    "user_growth_rate": round((new_users_30d / max(total_users - new_users_30d, 1)) * 100, 2),
                    "listing_growth_rate": round((new_listings_30d / max(total_listings - new_listings_30d, 1)) * 100, 2)
                },
                "revenue": {
                    "total_revenue": revenue_data["total_revenue"],
                    "subscription_revenue": revenue_data["subscription_revenue"],
                    "listing_revenue": revenue_data["listing_revenue"],
                    "average_revenue_per_user": round(revenue_data["total_revenue"] / max(total_users, 1), 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting platform overview: {str(e)}")
            return {}

    @staticmethod
    async def get_user_analytics(user_id: str) -> Dict[str, Any]:
        """Get detailed analytics for a specific user"""
        try:
            user = db.users.find_one({"user_id": user_id})
            if not user:
                return {}
            
            # User's listings analytics
            user_listings = list(db.listings.find({"user_id": user_id}))
            total_listings = len(user_listings)
            active_listings = len([l for l in user_listings if l.get("status") == "active"])
            featured_listings = len([l for l in user_listings if l.get("is_featured")])
            
            # Connection analytics
            connections_received = db.connections.count_documents({"listing_owner_id": user_id})
            connections_made = db.connections.count_documents({"requester_id": user_id})
            successful_connections = db.connections.count_documents({
                "$or": [
                    {"listing_owner_id": user_id, "status": "accepted"},
                    {"requester_id": user_id, "status": "accepted"}
                ]
            })
            
            # Payment history
            payments = list(db.payments.find({"user_id": user_id}, {"_id": 0}))
            total_spent = sum(p.get("amount", 0) for p in payments if p.get("status") == "completed")
            
            # Product type breakdown
            product_breakdown = defaultdict(int)
            for listing in user_listings:
                product_type = listing.get("product_type", "unknown")
                product_breakdown[product_type] += 1
            
            # Performance metrics
            avg_connections_per_listing = round(connections_received / max(total_listings, 1), 2)
            connection_success_rate = round((successful_connections / max(connections_received + connections_made, 1)) * 100, 2)
            
            return {
                "user_info": {
                    "user_id": user_id,
                    "company_name": user.get("company_name"),
                    "country": user.get("country"),
                    "role": user.get("role"),
                    "trading_role": user.get("trading_role"),
                    "member_since": user.get("created_at")
                },
                "listings": {
                    "total_listings": total_listings,
                    "active_listings": active_listings,
                    "featured_listings": featured_listings,
                    "product_breakdown": dict(product_breakdown)
                },
                "connections": {
                    "connections_received": connections_received,
                    "connections_made": connections_made,
                    "successful_connections": successful_connections,
                    "avg_connections_per_listing": avg_connections_per_listing,
                    "connection_success_rate": connection_success_rate
                },
                "financial": {
                    "total_spent": total_spent,
                    "payment_history": payments,
                    "subscription_status": user.get("subscription_status", "basic")
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user analytics: {str(e)}")
            return {}

    @staticmethod
    async def get_market_analytics() -> Dict[str, Any]:
        """Get market analytics and trends"""
        try:
            # Product type distribution
            product_pipeline = list(db.listings.aggregate([
                {"$group": {
                    "_id": "$product_type",
                    "count": {"$sum": 1},
                    "avg_quantity": {"$avg": "$quantity"}
                }},
                {"$sort": {"count": -1}}
            ]))
            
            # Geographic distribution
            geo_pipeline = list(db.users.aggregate([
                {"$group": {
                    "_id": "$country",
                    "trader_count": {"$sum": 1},
                    "listing_count": {"$sum": {"$size": {"$ifNull": ["$listings", []]}}}
                }},
                {"$sort": {"trader_count": -1}},
                {"$limit": 10}
            ]))
            
            # Trading hub activity
            hub_pipeline = list(db.listings.aggregate([
                {"$group": {
                    "_id": "$trading_hub",
                    "listing_count": {"$sum": 1},
                    "total_quantity": {"$sum": "$quantity"}
                }},
                {"$sort": {"listing_count": -1}}
            ]))
            
            # Price analysis (mock data - in real implementation would connect to market APIs)
            price_trends = {
                "crude_oil": {
                    "current_avg": 78.50,
                    "weekly_change": 2.3,
                    "monthly_change": -1.2,
                    "volatility": "moderate"
                },
                "natural_gas": {
                    "current_avg": 2.85,
                    "weekly_change": -0.15,
                    "monthly_change": 0.8,
                    "volatility": "high"
                },
                "lng": {
                    "current_avg": 12.45,
                    "weekly_change": 0.95,
                    "monthly_change": 3.2,
                    "volatility": "low"
                }
            }
            
            # Activity trends
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            daily_activity = list(db.listings.aggregate([
                {"$match": {"created_at": {"$gte": thirty_days_ago}}},
                {"$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "new_listings": {"$sum": 1}
                }},
                {"$sort": {"_id": 1}}
            ]))
            
            return {
                "product_distribution": [
                    {
                        "product_type": item["_id"],
                        "listing_count": item["count"],
                        "avg_quantity": round(item["avg_quantity"], 2)
                    }
                    for item in product_pipeline
                ],
                "geographic_distribution": [
                    {
                        "country": item["_id"],
                        "trader_count": item["trader_count"],
                        "listing_count": item["listing_count"]
                    }
                    for item in geo_pipeline
                ],
                "trading_hub_activity": [
                    {
                        "hub": item["_id"],
                        "listing_count": item["listing_count"],
                        "total_quantity": item["total_quantity"]
                    }
                    for item in hub_pipeline
                ],
                "price_trends": price_trends,
                "activity_trends": [
                    {
                        "date": item["_id"],
                        "new_listings": item["new_listings"]
                    }
                    for item in daily_activity
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting market analytics: {str(e)}")
            return {}

    @staticmethod
    async def get_revenue_analytics() -> Dict[str, Any]:
        """Get detailed revenue analytics"""
        try:
            now = datetime.utcnow()
            
            # Monthly revenue breakdown
            monthly_revenue = list(db.payments.aggregate([
                {"$match": {"status": "completed"}},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$created_at"},
                        "month": {"$month": "$created_at"}
                    },
                    "total_revenue": {"$sum": "$amount"},
                    "subscription_revenue": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$payment_type", "subscription"]},
                                "$amount",
                                0
                            ]
                        }
                    },
                    "listing_revenue": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$payment_type", "featured_listing"]},
                                "$amount",
                                0
                            ]
                        }
                    },
                    "transaction_count": {"$sum": 1}
                }},
                {"$sort": {"_id.year": -1, "_id.month": -1}},
                {"$limit": 12}
            ]))
            
            # Subscription tier breakdown
            subscription_tiers = list(db.payments.aggregate([
                {"$match": {
                    "payment_type": "subscription",
                    "status": {"$in": ["completed", "active"]}
                }},
                {"$group": {
                    "_id": "$subscription_tier",
                    "subscriber_count": {"$sum": 1},
                    "total_revenue": {"$sum": "$amount"}
                }}
            ]))
            
            # Customer lifetime value
            clv_analysis = list(db.payments.aggregate([
                {"$match": {"status": "completed"}},
                {"$group": {
                    "_id": "$user_id",
                    "total_spent": {"$sum": "$amount"},
                    "transaction_count": {"$sum": 1},
                    "first_payment": {"$min": "$created_at"},
                    "last_payment": {"$max": "$created_at"}
                }},
                {"$group": {
                    "_id": None,
                    "avg_clv": {"$avg": "$total_spent"},
                    "avg_transactions": {"$avg": "$transaction_count"},
                    "total_customers": {"$sum": 1}
                }}
            ]))
            
            clv_data = clv_analysis[0] if clv_analysis else {
                "avg_clv": 0,
                "avg_transactions": 0,
                "total_customers": 0
            }
            
            # Revenue forecasting (simple projection based on growth)
            recent_monthly = monthly_revenue[:3] if len(monthly_revenue) >= 3 else monthly_revenue
            if len(recent_monthly) >= 2:
                growth_rate = (recent_monthly[0]["total_revenue"] - recent_monthly[1]["total_revenue"]) / max(recent_monthly[1]["total_revenue"], 1)
                projected_next_month = recent_monthly[0]["total_revenue"] * (1 + growth_rate)
            else:
                growth_rate = 0
                projected_next_month = 0
            
            return {
                "monthly_breakdown": [
                    {
                        "month": f"{item['_id']['year']}-{item['_id']['month']:02d}",
                        "total_revenue": item["total_revenue"],
                        "subscription_revenue": item["subscription_revenue"],
                        "listing_revenue": item["listing_revenue"],
                        "transaction_count": item["transaction_count"]
                    }
                    for item in monthly_revenue
                ],
                "subscription_tiers": [
                    {
                        "tier": item["_id"] or "unknown",
                        "subscriber_count": item["subscriber_count"],
                        "total_revenue": item["total_revenue"]
                    }
                    for item in subscription_tiers
                ],
                "customer_metrics": {
                    "average_clv": round(clv_data["avg_clv"], 2),
                    "average_transactions_per_customer": round(clv_data["avg_transactions"], 2),
                    "total_paying_customers": clv_data["total_customers"]
                },
                "projections": {
                    "monthly_growth_rate": round(growth_rate * 100, 2),
                    "projected_next_month_revenue": round(projected_next_month, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting revenue analytics: {str(e)}")
            return {}

    @staticmethod
    async def get_listing_performance(listing_id: str) -> Dict[str, Any]:
        """Get performance analytics for a specific listing"""
        try:
            listing = db.listings.find_one({"listing_id": listing_id})
            if not listing:
                return {}
            
            # Connection metrics
            total_connections = db.connections.count_documents({"listing_id": listing_id})
            accepted_connections = db.connections.count_documents({
                "listing_id": listing_id,
                "status": "accepted"
            })
            
            # Time-based analytics
            created_at = listing.get("created_at")
            days_active = (datetime.utcnow() - created_at).days if created_at else 0
            
            # Performance scores
            connection_rate = round((total_connections / max(days_active, 1)) * 7, 2)  # connections per week
            success_rate = round((accepted_connections / max(total_connections, 1)) * 100, 2)
            
            # Comparison with similar listings
            similar_listings = list(db.listings.aggregate([
                {"$match": {
                    "product_type": listing.get("product_type"),
                    "listing_id": {"$ne": listing_id}
                }},
                {"$lookup": {
                    "from": "connections",
                    "localField": "listing_id",
                    "foreignField": "listing_id",
                    "as": "connections"
                }},
                {"$addFields": {
                    "connection_count": {"$size": "$connections"}
                }},
                {"$group": {
                    "_id": None,
                    "avg_connections": {"$avg": "$connection_count"},
                    "max_connections": {"$max": "$connection_count"}
                }}
            ]))
            
            benchmark_data = similar_listings[0] if similar_listings else {
                "avg_connections": 0,
                "max_connections": 0
            }
            
            return {
                "listing_info": {
                    "listing_id": listing_id,
                    "title": listing.get("title"),
                    "product_type": listing.get("product_type"),
                    "is_featured": listing.get("is_featured", False),
                    "status": listing.get("status"),
                    "created_at": created_at,
                    "days_active": days_active
                },
                "performance_metrics": {
                    "total_connections": total_connections,
                    "accepted_connections": accepted_connections,
                    "connection_rate_per_week": connection_rate,
                    "success_rate_percentage": success_rate
                },
                "benchmarks": {
                    "avg_connections_similar_listings": round(benchmark_data["avg_connections"], 2),
                    "max_connections_similar_listings": benchmark_data["max_connections"],
                    "performance_vs_average": round((total_connections / max(benchmark_data["avg_connections"], 1)) * 100, 2)
                },
                "recommendations": AnalyticsService._get_listing_recommendations(
                    total_connections, 
                    success_rate, 
                    listing.get("is_featured", False),
                    days_active
                )
            }
            
        except Exception as e:
            logger.error(f"Error getting listing performance: {str(e)}")
            return {}

    @staticmethod
    def _get_listing_recommendations(connections: int, success_rate: float, is_featured: bool, days_active: int) -> List[str]:
        """Generate recommendations for improving listing performance"""
        recommendations = []
        
        if connections < 3 and days_active > 7:
            recommendations.append("Consider updating your listing title and description to be more specific and attractive")
            
        if success_rate < 50 and connections > 5:
            recommendations.append("Your listing gets interest but low conversion. Review your pricing and terms")
            
        if not is_featured and connections > 10:
            recommendations.append("Your listing is popular! Consider upgrading to featured for even more visibility")
            
        if days_active > 30 and connections < 5:
            recommendations.append("Try updating your listing with current market prices and fresh description")
            
        if success_rate > 80:
            recommendations.append("Excellent performance! Consider creating similar listings")
            
        if len(recommendations) == 0:
            recommendations.append("Your listing is performing well. Keep monitoring and updating as needed")
            
        return recommendations

# Create global analytics service instance
analytics_service = AnalyticsService()
