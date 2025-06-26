"""
MongoDB Query Optimization and Performance Monitoring
Enhanced database performance with intelligent query optimization
"""

from pymongo import MongoClient
from typing import Dict, List, Any, Optional, Tuple
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
import os

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Intelligent MongoDB query optimizer with performance monitoring
    """
    
    def __init__(self, mongo_url: str = None):
        self.mongo_url = mongo_url or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = MongoClient(self.mongo_url)
        self.db = self.client.oil_gas_finder
        self.query_stats = {}
        self.slow_query_threshold = 100  # milliseconds
    
    def monitor_query_performance(self, collection_name: str):
        """Decorator to monitor query performance"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Log slow queries
                    if execution_time > self.slow_query_threshold:
                        logger.warning(
                            f"Slow query detected: {func.__name__} on {collection_name} "
                            f"took {execution_time:.2f}ms"
                        )
                    
                    # Update query statistics
                    if collection_name not in self.query_stats:
                        self.query_stats[collection_name] = {
                            'total_queries': 0,
                            'total_time': 0,
                            'slow_queries': 0,
                            'avg_time': 0
                        }
                    
                    stats = self.query_stats[collection_name]
                    stats['total_queries'] += 1
                    stats['total_time'] += execution_time
                    if execution_time > self.slow_query_threshold:
                        stats['slow_queries'] += 1
                    stats['avg_time'] = stats['total_time'] / stats['total_queries']
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Query failed: {func.__name__} on {collection_name}: {e}")
                    raise
            
            return wrapper
        return decorator
    
    def optimize_user_queries(self):
        """Optimized user-related queries"""
        
        @self.monitor_query_performance('users')
        def find_user_by_email(email: str) -> Optional[Dict]:
            """Optimized user lookup by email"""
            return self.db.users.find_one(
                {"email": email},
                {"password_hash": 1, "user_id": 1, "role": 1, "first_name": 1, "last_name": 1}
            )
        
        @self.monitor_query_performance('users')
        def find_user_by_id(user_id: str) -> Optional[Dict]:
            """Optimized user lookup by ID"""
            return self.db.users.find_one(
                {"user_id": user_id},
                {"password_hash": 0}  # Exclude sensitive data
            )
        
        @self.monitor_query_performance('users')
        def get_users_by_role(role: str, limit: int = 100) -> List[Dict]:
            """Get users by role with pagination"""
            return list(self.db.users.find(
                {"role": role},
                {"password_hash": 0, "login_attempts": 0}
            ).limit(limit).sort("created_at", -1))
        
        return {
            'find_user_by_email': find_user_by_email,
            'find_user_by_id': find_user_by_id,
            'get_users_by_role': get_users_by_role
        }
    
    def optimize_listing_queries(self):
        """Optimized trading listing queries"""
        
        @self.monitor_query_performance('listings')
        def search_listings(filters: Dict[str, Any], skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
            """Optimized listing search with aggregation pipeline"""
            pipeline = []
            
            # Build match stage
            match_conditions = {"status": {"$in": ["active", "featured"]}}
            
            if filters.get('product_type'):
                match_conditions["product_type"] = filters['product_type']
            
            if filters.get('trading_hub'):
                match_conditions["trading_hub"] = {"$regex": filters['trading_hub'], "$options": "i"}
            
            if filters.get('location'):
                match_conditions["location"] = {"$regex": filters['location'], "$options": "i"}
            
            if filters.get('min_quantity'):
                match_conditions["quantity"] = {"$gte": float(filters['min_quantity'])}
            
            if filters.get('max_quantity'):
                if "quantity" in match_conditions:
                    match_conditions["quantity"]["$lte"] = float(filters['max_quantity'])
                else:
                    match_conditions["quantity"] = {"$lte": float(filters['max_quantity'])}
            
            pipeline.append({"$match": match_conditions})
            
            # Add lookup for user information
            pipeline.append({
                "$lookup": {
                    "from": "users",
                    "localField": "user_id",
                    "foreignField": "user_id",
                    "as": "user_info",
                    "pipeline": [
                        {"$project": {"first_name": 1, "last_name": 1, "company_name": 1}}
                    ]
                }
            })
            
            # Sort by featured status and creation date
            pipeline.append({
                "$sort": {
                    "status": 1,  # Featured first
                    "created_at": -1
                }
            })
            
            # Get total count
            count_pipeline = pipeline + [{"$count": "total"}]
            count_result = list(self.db.listings.aggregate(count_pipeline))
            total_count = count_result[0]["total"] if count_result else 0
            
            # Add pagination
            pipeline.extend([
                {"$skip": skip},
                {"$limit": limit}
            ])
            
            # Execute query
            results = list(self.db.listings.aggregate(pipeline))
            
            return results, total_count
        
        @self.monitor_query_performance('listings')
        def get_user_listings(user_id: str, limit: int = 50) -> List[Dict]:
            """Get user's listings efficiently"""
            return list(self.db.listings.find(
                {"user_id": user_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit))
        
        @self.monitor_query_performance('listings')
        def get_featured_listings(limit: int = 10) -> List[Dict]:
            """Get featured listings for homepage"""
            return list(self.db.listings.find(
                {"status": "featured"},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit))
        
        @self.monitor_query_performance('listings')
        def get_market_summary(commodity: str = None) -> Dict[str, Any]:
            """Get market summary using aggregation"""
            match_stage = {"status": {"$in": ["active", "featured"]}}
            if commodity:
                match_stage["product_type"] = commodity
            
            pipeline = [
                {"$match": match_stage},
                {"$group": {
                    "_id": "$product_type",
                    "total_listings": {"$sum": 1},
                    "avg_quantity": {"$avg": "$quantity"},
                    "total_quantity": {"$sum": "$quantity"},
                    "unique_companies": {"$addToSet": "$company_name"}
                }},
                {"$project": {
                    "commodity": "$_id",
                    "total_listings": 1,
                    "avg_quantity": {"$round": ["$avg_quantity", 2]},
                    "total_quantity": 1,
                    "unique_companies": {"$size": "$unique_companies"},
                    "_id": 0
                }}
            ]
            
            results = list(self.db.listings.aggregate(pipeline))
            return results
        
        return {
            'search_listings': search_listings,
            'get_user_listings': get_user_listings,
            'get_featured_listings': get_featured_listings,
            'get_market_summary': get_market_summary
        }
    
    def optimize_analytics_queries(self):
        """Optimized analytics queries"""
        
        @self.monitor_query_performance('analytics_pageviews')
        def get_pageview_analytics(
            start_date: datetime,
            end_date: datetime,
            page: str = None
        ) -> Dict[str, Any]:
            """Get pageview analytics with time-based aggregation"""
            match_conditions = {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
            
            if page:
                match_conditions["page"] = page
            
            pipeline = [
                {"$match": match_conditions},
                {"$group": {
                    "_id": {
                        "year": {"$year": "$timestamp"},
                        "month": {"$month": "$timestamp"},
                        "day": {"$dayOfMonth": "$timestamp"},
                        "page": "$page"
                    },
                    "views": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$project": {
                    "date": {
                        "$dateFromParts": {
                            "year": "$_id.year",
                            "month": "$_id.month",
                            "day": "$_id.day"
                        }
                    },
                    "page": "$_id.page",
                    "views": 1,
                    "unique_users": {"$size": "$unique_users"},
                    "_id": 0
                }},
                {"$sort": {"date": 1}}
            ]
            
            return list(self.db.analytics_pageviews.aggregate(pipeline))
        
        @self.monitor_query_performance('analytics_events')
        def get_conversion_analytics(
            start_date: datetime,
            end_date: datetime
        ) -> Dict[str, Any]:
            """Get conversion funnel analytics"""
            pipeline = [
                {"$match": {
                    "timestamp": {"$gte": start_date, "$lte": end_date},
                    "event_type": {"$in": ["registration", "listing_created", "premium_upgrade"]}
                }},
                {"$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                    "unique_users": {"$addToSet": "$user_id"}
                }},
                {"$project": {
                    "event_type": "$_id",
                    "count": 1,
                    "unique_users": {"$size": "$unique_users"},
                    "_id": 0
                }}
            ]
            
            return list(self.db.analytics_events.aggregate(pipeline))
        
        return {
            'get_pageview_analytics': get_pageview_analytics,
            'get_conversion_analytics': get_conversion_analytics
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate database performance report"""
        report = {
            "query_statistics": self.query_stats,
            "collection_stats": {},
            "index_usage": {},
            "recommendations": []
        }
        
        # Get collection statistics
        for collection_name in ['users', 'listings', 'analytics_pageviews', 'analytics_events']:
            try:
                stats = self.db.command("collStats", collection_name)
                report["collection_stats"][collection_name] = {
                    "count": stats.get("count", 0),
                    "size": stats.get("size", 0),
                    "avgObjSize": stats.get("avgObjSize", 0),
                    "storageSize": stats.get("storageSize", 0),
                    "totalIndexSize": stats.get("totalIndexSize", 0)
                }
            except Exception as e:
                logger.error(f"Failed to get stats for {collection_name}: {e}")
        
        # Check index usage
        try:
            index_stats = self.db.command("collStats", "listings", indexDetails=True)
            report["index_usage"] = index_stats.get("indexSizes", {})
        except Exception as e:
            logger.error(f"Failed to get index usage: {e}")
        
        # Generate recommendations
        if self.query_stats:
            for collection, stats in self.query_stats.items():
                if stats["slow_queries"] > stats["total_queries"] * 0.1:  # More than 10% slow queries
                    report["recommendations"].append(
                        f"Consider optimizing queries for {collection} collection - "
                        f"{stats['slow_queries']} slow queries out of {stats['total_queries']}"
                    )
        
        return report
    
    def cleanup_old_analytics(self, days_to_keep: int = 90):
        """Clean up old analytics data to maintain performance"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean pageviews
        pageview_result = self.db.analytics_pageviews.delete_many(
            {"timestamp": {"$lt": cutoff_date}}
        )
        
        # Clean events
        events_result = self.db.analytics_events.delete_many(
            {"timestamp": {"$lt": cutoff_date}}
        )
        
        logger.info(
            f"Cleaned up analytics data: "
            f"{pageview_result.deleted_count} pageviews, "
            f"{events_result.deleted_count} events"
        )
        
        return {
            "pageviews_deleted": pageview_result.deleted_count,
            "events_deleted": events_result.deleted_count
        }

# Global query optimizer instance
query_optimizer = QueryOptimizer()

# Export optimized query functions
user_queries = query_optimizer.optimize_user_queries()
listing_queries = query_optimizer.optimize_listing_queries()
analytics_queries = query_optimizer.optimize_analytics_queries()

__all__ = [
    'QueryOptimizer',
    'query_optimizer',
    'user_queries',
    'listing_queries',
    'analytics_queries'
]