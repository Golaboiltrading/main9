# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/oilgas')
client = MongoClient(MONGO_URL)
db = client.oilgas
users_collection = db.users
listings_collection = db.listings
analytics_collection = db.analytics
subscriptions_collection = db.subscriptions

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    try:
        # Test database connection
        db.command('ping')
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": "disconnected",
                "error": str(e)
            }
        )