"""
Database Performance Optimization Script
Creates indexes for improved query performance
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, TEXT
import os
import logging

logger = logging.getLogger(__name__)

def create_database_indexes():
    """
    Create performance-optimized indexes for the Oil & Gas Finder database
    """
    try:
        # Connect to MongoDB
        MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        client = MongoClient(MONGO_URL)
        db = client.oil_gas_finder
        
        print("🚀 Creating performance-optimized database indexes...")
        
        # Users collection indexes
        users_collection = db.users
        
        # Unique index on email for fast login lookups
        users_collection.create_index([("email", ASCENDING)], unique=True, background=True)
        
        # Index on user_id for fast user lookups
        users_collection.create_index([("user_id", ASCENDING)], unique=True, background=True)
        
        # Compound index for role-based queries
        users_collection.create_index([("role", ASCENDING), ("created_at", DESCENDING)], background=True)
        
        # Index for login attempt tracking (security feature)
        users_collection.create_index([("login_attempts", ASCENDING), ("account_locked", ASCENDING)], background=True)
        
        print("✅ Users collection indexes created")
        
        # Listings collection indexes
        listings_collection = db.listings
        
        # Unique index on listing_id
        listings_collection.create_index([("listing_id", ASCENDING)], unique=True, background=True)
        
        # Compound index for trading searches (most common query pattern)
        listings_collection.create_index([
            ("product_type", ASCENDING),
            ("trading_hub", ASCENDING),
            ("status", ASCENDING),
            ("created_at", DESCENDING)
        ], background=True)
        
        # Index for user's listings
        listings_collection.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)], background=True)
        
        # Index for featured listings
        listings_collection.create_index([("status", ASCENDING), ("created_at", DESCENDING)], background=True)
        
        # Text index for search functionality
        listings_collection.create_index([
            ("title", TEXT),
            ("description", TEXT),
            ("company_name", TEXT)
        ], background=True)
        
        # Index for price and quantity range queries
        listings_collection.create_index([("quantity", ASCENDING)], background=True)
        
        # Geospatial index for location-based queries
        listings_collection.create_index([("location", ASCENDING), ("trading_hub", ASCENDING)], background=True)
        
        print("✅ Listings collection indexes created")
        
        # Analytics collections indexes
        analytics_pageviews = db.analytics_pageviews
        analytics_events = db.analytics_events
        
        # Time-series indexes for analytics (most recent first)
        analytics_pageviews.create_index([("timestamp", DESCENDING)], background=True)
        analytics_pageviews.create_index([("page", ASCENDING), ("timestamp", DESCENDING)], background=True)
        analytics_pageviews.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], background=True)
        
        analytics_events.create_index([("timestamp", DESCENDING)], background=True)
        analytics_events.create_index([("event_type", ASCENDING), ("timestamp", DESCENDING)], background=True)
        analytics_events.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], background=True)
        
        print("✅ Analytics collection indexes created")
        
        # Subscriptions collection indexes
        subscriptions_collection = db.subscriptions
        
        # Index on user_id for subscription lookups
        subscriptions_collection.create_index([("user_id", ASCENDING)], background=True)
        
        # Index for subscription status and expiry tracking
        subscriptions_collection.create_index([
            ("status", ASCENDING),
            ("expires_at", ASCENDING)
        ], background=True)
        
        # Index for subscription type analytics
        subscriptions_collection.create_index([("plan_type", ASCENDING), ("created_at", DESCENDING)], background=True)
        
        print("✅ Subscriptions collection indexes created")
        
        # Connections collection indexes
        connections_collection = db.connections
        
        # Compound index for connection queries
        connections_collection.create_index([("requester_id", ASCENDING), ("status", ASCENDING)], background=True)
        connections_collection.create_index([("recipient_id", ASCENDING), ("status", ASCENDING)], background=True)
        
        # Index for connection timestamps
        connections_collection.create_index([("created_at", DESCENDING)], background=True)
        
        print("✅ Connections collection indexes created")
        
        # Newsletter and leads collections indexes
        newsletter_subscribers = db.newsletter_subscribers
        leads_collection = db.leads
        
        # Unique index on email for newsletter
        newsletter_subscribers.create_index([("email", ASCENDING)], unique=True, background=True)
        newsletter_subscribers.create_index([("subscribed_at", DESCENDING)], background=True)
        
        # Leads tracking indexes
        leads_collection.create_index([("email", ASCENDING), ("created_at", DESCENDING)], background=True)
        leads_collection.create_index([("source", ASCENDING), ("created_at", DESCENDING)], background=True)
        leads_collection.create_index([("status", ASCENDING), ("created_at", DESCENDING)], background=True)
        
        print("✅ Newsletter and leads collection indexes created")
        
        # Companies collection indexes
        companies_collection = db.companies
        
        # Index on user_id for company profile lookups
        companies_collection.create_index([("user_id", ASCENDING)], unique=True, background=True)
        
        # Text index for company search
        companies_collection.create_index([
            ("company_name", TEXT),
            ("description", TEXT)
        ], background=True)
        
        # Index for trading hubs and certifications
        companies_collection.create_index([("trading_hubs", ASCENDING)], background=True)
        companies_collection.create_index([("country", ASCENDING)], background=True)
        
        print("✅ Companies collection indexes created")
        
        # Security audit log collection (if exists)
        try:
            security_logs = db.security_logs
            security_logs.create_index([("timestamp", DESCENDING)], background=True)
            security_logs.create_index([("event_type", ASCENDING), ("timestamp", DESCENDING)], background=True)
            security_logs.create_index([("user_id", ASCENDING), ("timestamp", DESCENDING)], background=True)
            security_logs.create_index([("severity", ASCENDING), ("timestamp", DESCENDING)], background=True)
            print("✅ Security logs collection indexes created")
        except Exception as e:
            print(f"⚠️  Security logs indexes skipped: {e}")
        
        print("\n🎉 All database indexes created successfully!")
        print("📊 Database performance optimization complete!")
        
        # Print index statistics
        print("\n📈 Index Statistics:")
        for collection_name in ['users', 'listings', 'analytics_pageviews', 'subscriptions']:
            collection = db[collection_name]
            indexes = list(collection.list_indexes())
            print(f"  {collection_name}: {len(indexes)} indexes")
        
        client.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database indexes: {e}")
        print(f"❌ Error creating indexes: {e}")
        return False

if __name__ == "__main__":
    create_database_indexes()