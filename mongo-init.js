// MongoDB initialization script for production
db = db.getSiblingDB('oilgasfinder');

// Create collections with proper indexes
db.createCollection('users');
db.createCollection('listings');
db.createCollection('connections');
db.createCollection('analytics_pageviews');
db.createCollection('analytics_events');
db.createCollection('leads');
db.createCollection('newsletter_subscribers');
db.createCollection('blog_posts');
db.createCollection('locations');
db.createCollection('products');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.listings.createIndex({ "user_id": 1 });
db.listings.createIndex({ "created_at": -1 });
db.listings.createIndex({ "product_type": 1 });
db.listings.createIndex({ "location": 1 });
db.connections.createIndex({ "user_id": 1 });
db.connections.createIndex({ "listing_id": 1 });
db.analytics_pageviews.createIndex({ "created_at": -1 });
db.analytics_events.createIndex({ "created_at": -1 });
db.leads.createIndex({ "email": 1 });
db.leads.createIndex({ "created_at": -1 });
db.newsletter_subscribers.createIndex({ "email": 1 }, { unique: true });
db.blog_posts.createIndex({ "slug": 1 }, { unique: true });
db.blog_posts.createIndex({ "category": 1 });
db.blog_posts.createIndex({ "published": 1 });

print('Database initialization completed successfully');
