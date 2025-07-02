"""
MongoDB Query Optimization and Performance Monitoring
Enhanced database performance with intelligent query optimization
"""

from motor.motor_asyncio import AsyncIOMotorClient # MODIFIED
from typing import Dict, List, Any, Optional, Tuple
import time
import logging
from datetime import datetime, timedelta
from functools import wraps
import os
import asyncio # MODIFIED

logger = logging.getLogger(__name__)

class QueryOptimizer:
    """
    Intelligent MongoDB query optimizer with performance monitoring
    """
    
    def __init__(self, mongo_url: str = None, db_name: str = "oil_gas_finder"): # MODIFIED to accept db_name
        self.mongo_url = mongo_url or os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.client = AsyncIOMotorClient(self.mongo_url) # MODIFIED
        self.db = self.client[db_name] # MODIFIED
        self.query_stats = {}
        self.slow_query_threshold = 100  # milliseconds
    
    def monitor_query_performance(self, collection_name: str):
        """Decorator to monitor query performance"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs): # MODIFIED to be async
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs) # MODIFIED to await async func
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
    
    async def optimize_user_queries(self): # MODIFIED to be async, also method name implies it returns functions
        """Optimized user-related queries"""
        
        @self.monitor_query_performance('users')
        async def find_user_by_email(email: str) -> Optional[Dict]: # MODIFIED
            """Optimized user lookup by email"""
            return await self.db.users.find_one( # MODIFIED
                {"email": email},
                {"password_hash": 1, "user_id": 1, "role": 1, "first_name": 1, "last_name": 1}
            )
        
        @self.monitor_query_performance('users')
        async def find_user_by_id(user_id: str) -> Optional[Dict]: # MODIFIED
            """Optimized user lookup by ID"""
            return await self.db.users.find_one( # MODIFIED
                {"user_id": user_id},
                {"password_hash": 0}  # Exclude sensitive data
            )
        
        @self.monitor_query_performance('users')
        async def get_users_by_role(role: str, limit: int = 100) -> List[Dict]: # MODIFIED
            """Get users by role with pagination"""
            cursor = self.db.users.find( # MODIFIED
                {"role": role},
                {"password_hash": 0, "login_attempts": 0}
            ).limit(limit).sort("created_at", -1)
            return await cursor.to_list(length=limit) # MODIFIED
        
        return {
            'find_user_by_email': find_user_by_email,
            'find_user_by_id': find_user_by_id,
            'get_users_by_role': get_users_by_role
        }
    
    async def optimize_listing_queries(self): # MODIFIED to be async
        """Optimized trading listing queries"""
        
        @self.monitor_query_performance('listings')
        async def search_listings(filters: Dict[str, Any], skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]: # MODIFIED
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
            count_result_cursor = self.db.listings.aggregate(count_pipeline) # MODIFIED
            count_result = await count_result_cursor.to_list(length=1) # MODIFIED
            total_count = count_result[0]["total"] if count_result else 0
            
            # Add pagination
            pipeline.extend([
                {"$skip": skip},
                {"$limit": limit}
            ])
            
            # Execute query
            results_cursor = self.db.listings.aggregate(pipeline) # MODIFIED
            results = await results_cursor.to_list(length=limit) # MODIFIED
            
            return results, total_count
        
        @self.monitor_query_performance('listings')
        async def get_user_listings(user_id: str, limit: int = 50) -> List[Dict]: # MODIFIED
            """Get user's listings efficiently"""
            cursor = self.db.listings.find( # MODIFIED
                {"user_id": user_id},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit)
            return await cursor.to_list(length=limit) # MODIFIED
        
        @self.monitor_query_performance('listings')
        async def get_featured_listings(limit: int = 10) -> List[Dict]: # MODIFIED
            """Get featured listings for homepage"""
            cursor = self.db.listings.find( # MODIFIED
                {"status": "featured"},
                {"_id": 0}
            ).sort("created_at", -1).limit(limit)
            return await cursor.to_list(length=limit) # MODIFIED
        
        @self.monitor_query_performance('listings')
        async def get_market_summary(commodity: str = None) -> Dict[str, Any]: # MODIFIED
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
            
            results_cursor = self.db.listings.aggregate(pipeline) # MODIFIED
            return await results_cursor.to_list(length=None) # MODIFIED
        
        return {
            'search_listings': search_listings,
            'get_user_listings': get_user_listings,
            'get_featured_listings': get_featured_listings,
            'get_market_summary': get_market_summary
        }
    
    async def optimize_analytics_queries(self): # MODIFIED to be async
        """Optimized analytics queries"""
        
        @self.monitor_query_performance('analytics_pageviews')
        async def get_pageview_analytics( # MODIFIED
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
            
            cursor = self.db.analytics_pageviews.aggregate(pipeline) # MODIFIED
            return await cursor.to_list(length=None) # MODIFIED
        
        @self.monitor_query_performance('analytics_events')
        async def get_conversion_analytics( # MODIFIED
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
            cursor = self.db.analytics_events.aggregate(pipeline) # MODIFIED
            return await cursor.to_list(length=None) # MODIFIED
        
        return {
            'get_pageview_analytics': get_pageview_analytics,
            'get_conversion_analytics': get_conversion_analytics
        }
    
    async def get_performance_report(self) -> Dict[str, Any]: # MODIFIED
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
                stats = await self.db.command("collStats", collection_name) # MODIFIED
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
            # collStats with indexDetails might not be directly awaitable if it's a command
            # For simplicity, this part is kept, but in a real scenario,
            # one might need to use run_command or ensure the client handles it.
            # Motor's command execution is typically `await db.command(...)`
            index_stats = await self.db.command("collStats", "listings", indexDetails=True) # MODIFIED
            report["index_usage"] = index_stats.get("indexSizes", {})
        except Exception as e:
            logger.error(f"Failed to get index usage: {e}")
        
        # Generate recommendations
        if self.query_stats:
            for collection, stats in self.query_stats.items():
                if stats["total_queries"] > 0 and stats["slow_queries"] > stats["total_queries"] * 0.1:  # More than 10% slow queries
                    report["recommendations"].append(
                        f"Consider optimizing queries for {collection} collection - "
                        f"{stats['slow_queries']} slow queries out of {stats['total_queries']}"
                    )
        
        return report
    
    async def cleanup_old_analytics(self, days_to_keep: int = 90): # MODIFIED
        """Clean up old analytics data to maintain performance"""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        # Clean pageviews
        pageview_result = await self.db.analytics_pageviews.delete_many( # MODIFIED
            {"timestamp": {"$lt": cutoff_date}}
        )
        
        # Clean events
        events_result = await self.db.analytics_events.delete_many( # MODIFIED
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

# It's better to initialize and export functions in an async context,
# or have the main app instantiate QueryOptimizer and fetch the methods.
# For now, we'll make the global instance and assume its methods will be
# populated by calling the async methods upon app startup or when first needed.

query_optimizer = QueryOptimizer(db_name="oil_gas_finder") # db_name from server.py

# These will now store async functions. Callers must await them.
# This initialization pattern might need adjustment depending on how server.py consumes them.
# A common pattern is to initialize these within an async function or make QueryOptimizer
# methods directly callable as async.

# This immediate call to populate user_queries etc. won't work as they are async.
# user_queries = query_optimizer.optimize_user_queries()
# listing_queries = query_optimizer.optimize_listing_queries()
# analytics_queries = query_optimizer.optimize_analytics_queries()

# Instead, we export the instance, and the consuming code (server.py)
# will call these methods and await their results to get the dict of functions.
# Or, more simply, server.py can directly call methods on the query_optimizer instance.

# For simplicity of refactoring server.py, we will pre-populate these.
# This requires an event loop to be running if we were to call them here.
# We'll assume server.py will handle the async nature of these when it imports them.

_optimized_queries_cache = {}

async def get_optimized_user_queries():
    if "user_queries" not in _optimized_queries_cache:
        _optimized_queries_cache["user_queries"] = await query_optimizer.optimize_user_queries()
    return _optimized_queries_cache["user_queries"]

async def get_optimized_listing_queries():
    if "listing_queries" not in _optimized_queries_cache:
        _optimized_queries_cache["listing_queries"] = await query_optimizer.optimize_listing_queries()
    return _optimized_queries_cache["listing_queries"]

async def get_optimized_analytics_queries():
    if "analytics_queries" not in _optimized_queries_cache:
        _optimized_queries_cache["analytics_queries"] = await query_optimizer.optimize_analytics_queries()
    return _optimized_queries_cache["analytics_queries"]


# The original export method was for synchronous functions.
# If server.py imports user_queries directly, it needs to be a dict of async functions.
# The QueryOptimizer methods (optimize_user_queries etc.) now return dicts of async functions.
# So server.py would do:
# from query_optimizer import query_optimizer # import instance
# user_query_funcs = await query_optimizer.optimize_user_queries()
# result = await user_query_funcs['find_user_by_email'](...)

# To maintain the existing import pattern in server.py (if it directly imports user_queries),
# we might need to adjust how these are exposed or how server.py uses them.
# For now, let's assume server.py will be adapted to call methods on the query_optimizer instance.

__all__ = [
    'QueryOptimizer',
    'query_optimizer', # Export the instance
    # The following are problematic for direct import if they need to be populated async
    # 'user_queries',
    # 'listing_queries',
    # 'analytics_queries'
    'get_optimized_user_queries', # Provide async getters
    'get_optimized_listing_queries',
    'get_optimized_analytics_queries'
]