from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pymongo import MongoClient
import os
import jwt
import hashlib
import secrets
import uuid
from passlib.context import CryptContext
import logging
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Import our new services separately to handle missing dependencies better
seo_router = None
analytics_router = None
content_router = None

try:
    from seo_routes import router as seo_router
except ImportError as e:
    print(f"Warning: Could not import SEO routes: {e}")
    seo_router = None

try:
    from analytics_routes import router as analytics_router
except ImportError as e:
    print(f"Warning: Could not import Analytics routes: {e}")
    analytics_router = None

try:
    from content_routes import router as content_router
except ImportError as e:
    print(f"Warning: Could not import Content routes: {e}")
    content_router = None

# Import other services
try:
    from paypal_service import PayPalService
    from email_service import email_service
    from analytics_service import analytics_service
    from business_growth_service import business_growth_service
    from content_marketing_service import content_marketing_service
except ImportError as e:
    print(f"Warning: Could not import advanced services: {e}")
    PayPalService = None
    email_service = None
    analytics_service = None
    business_growth_service = None
    content_marketing_service = None

# Initialize FastAPI app
app = FastAPI(title="Oil & Gas Finder API", version="1.0.0")

# Include SEO router if available
if seo_router:
    app.include_router(seo_router, tags=["SEO"])

# Include Analytics router if available
if analytics_router:
    app.include_router(analytics_router, tags=["Analytics"])

# Include Content router if available  
if content_router:
    app.include_router(content_router, tags=["Content"])

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security and configuration
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "oil-gas-finder-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder

# Collections
users_collection = db.users
companies_collection = db.companies
listings_collection = db.listings
connections_collection = db.connections
subscriptions_collection = db.subscriptions

# Enums
class UserRole(str, Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class ProductType(str, Enum):
    CRUDE_OIL = "crude_oil"
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    JET_FUEL = "jet_fuel"
    NATURAL_GAS = "natural_gas"
    LNG = "lng"
    LPG = "lpg"
    GAS_CONDENSATE = "gas_condensate"

class TradingRole(str, Enum):
    BUYER = "buyer"
    SELLER = "seller"
    BOTH = "both"

class ListingStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FEATURED = "featured"

# Pydantic models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    company_name: str
    phone: Optional[str] = None
    country: str
    trading_role: TradingRole

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class CompanyProfile(BaseModel):
    company_name: str
    description: Optional[str] = None
    website: Optional[str] = None
    phone: str
    address: str
    country: str
    trading_hubs: List[str] = []
    certifications: List[str] = []

class TradingListing(BaseModel):
    title: str
    product_type: ProductType
    quantity: float
    unit: str
    price_range: str
    location: str
    trading_hub: str
    description: str
    contact_person: str
    contact_email: EmailStr
    contact_phone: str
    is_featured: bool = False

class SearchFilters(BaseModel):
    product_type: Optional[ProductType] = None
    trading_role: Optional[TradingRole] = None
    location: Optional[str] = None
    trading_hub: Optional[str] = None
    min_quantity: Optional[float] = None
    max_quantity: Optional[float] = None

class PremiumSubscription(BaseModel):
    user_id: str
    plan_type: str  # "premium_basic", "premium_advanced", "enterprise"
    price: float
    duration_months: int

# Utility functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# API Endpoints

@app.get("/api/status")
async def get_status():
    return {"status": "Oil & Gas Finder API is running", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register")
async def register_user(user_data: UserCreate):
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    user_doc = {
        "user_id": user_id,
        "email": user_data.email,
        "password_hash": hashed_password,
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "company_name": user_data.company_name,
        "phone": user_data.phone,
        "country": user_data.country,
        "trading_role": user_data.trading_role,
        "role": UserRole.BASIC,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    users_collection.insert_one(user_doc)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    # Send welcome email
    if email_service:
        try:
            await email_service.send_welcome_email(user_data.email, user_data.first_name)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
    
    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "role": UserRole.BASIC
        }
    }

@app.post("/api/auth/login")
async def login_user(user_data: UserLogin):
    user = users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Update last login
    users_collection.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"]}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user["role"],
            "company_name": user["company_name"],
            "trading_role": user["trading_role"]
        }
    }

@app.get("/api/user/profile")
async def get_user_profile(user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"user_id": user_id}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove MongoDB _id field
    user.pop("_id", None)
    return user

@app.put("/api/user/profile")
async def update_user_profile(profile_data: CompanyProfile, user_id: str = Depends(get_current_user)):
    update_data = profile_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": update_data}
    )
    
    return {"message": "Profile updated successfully"}

@app.post("/api/listings")
async def create_listing(listing_data: TradingListing, user_id: str = Depends(get_current_user)):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    listing_id = str(uuid.uuid4())
    listing_doc = {
        "listing_id": listing_id,
        "user_id": user_id,
        "company_name": user["company_name"],
        "status": ListingStatus.FEATURED if listing_data.is_featured else ListingStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        **listing_data.dict()
    }
    
    listings_collection.insert_one(listing_doc)
    
    # Send listing approval email
    if email_service:
        try:
            await email_service.send_listing_approval(
                user["email"],
                user["first_name"],
                listing_data.title,
                listing_data.is_featured
            )
        except Exception as e:
            print(f"Failed to send listing approval email: {e}")
    
    return {
        "message": "Listing created successfully",
        "listing_id": listing_id
    }

@app.get("/api/listings")
async def get_listings(
    skip: int = 0,
    limit: int = 20,
    product_type: Optional[str] = None,
    location: Optional[str] = None,
    trading_hub: Optional[str] = None
):
    query = {"status": {"$in": [ListingStatus.ACTIVE, ListingStatus.FEATURED]}}
    
    if product_type:
        query["product_type"] = product_type
    if location:
        query["location"] = {"$regex": location, "$options": "i"}
    if trading_hub:
        query["trading_hub"] = {"$regex": trading_hub, "$options": "i"}
    
    # Featured listings first, then by creation date
    listings = list(
        listings_collection.find(query, {"_id": 0})
        .sort([("status", -1), ("created_at", -1)])
        .skip(skip)
        .limit(limit)
    )
    
    total_count = listings_collection.count_documents(query)
    
    return {
        "listings": listings,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

@app.get("/api/listings/my")
async def get_my_listings(user_id: str = Depends(get_current_user)):
    listings = list(
        listings_collection.find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
    )
    
    return {"listings": listings}

@app.put("/api/listings/{listing_id}")
async def update_listing(
    listing_id: str,
    listing_data: TradingListing,
    user_id: str = Depends(get_current_user)
):
    existing_listing = listings_collection.find_one({"listing_id": listing_id, "user_id": user_id})
    if not existing_listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    update_data = listing_data.dict()
    update_data["updated_at"] = datetime.utcnow()
    
    listings_collection.update_one(
        {"listing_id": listing_id},
        {"$set": update_data}
    )
    
    return {"message": "Listing updated successfully"}

@app.delete("/api/listings/{listing_id}")
async def delete_listing(listing_id: str, user_id: str = Depends(get_current_user)):
    result = listings_collection.delete_one({"listing_id": listing_id, "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {"message": "Listing deleted successfully"}

@app.post("/api/connections/{listing_id}")
async def create_connection(listing_id: str, user_id: str = Depends(get_current_user)):
    listing = listings_collection.find_one({"listing_id": listing_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing["user_id"] == user_id:
        raise HTTPException(status_code=400, detail="Cannot connect to your own listing")
    
    # Check if connection already exists
    existing_connection = connections_collection.find_one({
        "listing_id": listing_id,
        "requester_id": user_id
    })
    
    if existing_connection:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    connection_id = str(uuid.uuid4())
    connection_doc = {
        "connection_id": connection_id,
        "listing_id": listing_id,
        "listing_owner_id": listing["user_id"],
        "requester_id": user_id,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "messages": []
    }
    
    connections_collection.insert_one(connection_doc)
    
    # Send connection request email to listing owner
    if email_service:
        try:
            listing_owner = users_collection.find_one({"user_id": listing["user_id"]})
            requester = users_collection.find_one({"user_id": user_id})
            
            if listing_owner and requester:
                await email_service.send_connection_request(
                    listing_owner["email"],
                    listing_owner["first_name"],
                    f"{requester['first_name']} {requester['last_name']} ({requester['company_name']})",
                    listing["title"]
                )
        except Exception as e:
            print(f"Failed to send connection request email: {e}")
    
    return {
        "message": "Connection request sent successfully",
        "connection_id": connection_id
    }

@app.get("/api/connections")
async def get_connections(user_id: str = Depends(get_current_user)):
    connections = list(
        connections_collection.find({
            "$or": [
                {"listing_owner_id": user_id},
                {"requester_id": user_id}
            ]
        }, {"_id": 0}).sort("created_at", -1)
    )
    
    return {"connections": connections}

@app.get("/api/stats")
async def get_platform_stats():
    total_traders = users_collection.count_documents({})
    active_listings = listings_collection.count_documents({"status": {"$in": [ListingStatus.ACTIVE, ListingStatus.FEATURED]}})
    successful_connections = connections_collection.count_documents({"status": "accepted"})
    premium_traders = users_collection.count_documents({"role": {"$ne": UserRole.BASIC}})
    featured_listings = listings_collection.count_documents({"status": ListingStatus.FEATURED})
    
    return {
        "oil_gas_traders": total_traders,
        "active_oil_listings": active_listings,
        "successful_connections": successful_connections,
        "premium_finders": premium_traders,
        "featured_opportunities": featured_listings
    }

@app.post("/api/subscriptions/upgrade")
async def upgrade_subscription(
    subscription_data: PremiumSubscription,
    user_id: str = Depends(get_current_user)
):
    # In a real implementation, this would integrate with PayPal
    subscription_id = str(uuid.uuid4())
    subscription_doc = {
        "subscription_id": subscription_id,
        "user_id": user_id,
        "plan_type": subscription_data.plan_type,
        "price": subscription_data.price,
        "duration_months": subscription_data.duration_months,
        "start_date": datetime.utcnow(),
        "end_date": datetime.utcnow() + timedelta(days=30 * subscription_data.duration_months),
        "status": "active",
        "payment_status": "pending"  # Would be updated after PayPal confirmation
    }
    
    subscriptions_collection.insert_one(subscription_doc)
    
    # Update user role
    new_role = UserRole.PREMIUM if "premium" in subscription_data.plan_type else UserRole.ENTERPRISE
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"role": new_role}}
    )
    
    return {
        "message": "Subscription upgrade initiated",
        "subscription_id": subscription_id,
        "payment_url": f"/api/payments/paypal/{subscription_id}"  # Placeholder for PayPal integration
    }

@app.get("/api/search/companies")
async def search_companies(
    q: Optional[str] = None,
    country: Optional[str] = None,
    trading_role: Optional[str] = None,
    skip: int = 0,
    limit: int = 20
):
    query = {}
    
    if q:
        query["$or"] = [
            {"company_name": {"$regex": q, "$options": "i"}},
            {"description": {"$regex": q, "$options": "i"}}
        ]
    
    if country:
        query["country"] = {"$regex": country, "$options": "i"}
    
    if trading_role:
        query["trading_role"] = trading_role
    
    companies = list(
        users_collection.find(query, {
            "_id": 0,
            "password_hash": 0,
            "email": 0  # Hide sensitive info in search
        }).skip(skip).limit(limit)
    )
    
    total_count = users_collection.count_documents(query)
    
    return {
        "companies": companies,
        "total": total_count,
        "skip": skip,
        "limit": limit
    }

@app.get("/api/market-data")
async def get_market_data():
    # In a real implementation, this would fetch from external APIs
    mock_data = {
        "oil_prices": {
            "wti_crude": {"price": 78.45, "change": "+1.23", "updated": datetime.utcnow()},
            "brent_crude": {"price": 82.15, "change": "+0.98", "updated": datetime.utcnow()},
            "dubai_crude": {"price": 81.23, "change": "+1.05", "updated": datetime.utcnow()}
        },
        "gas_prices": {
            "natural_gas": {"price": 2.85, "change": "-0.12", "updated": datetime.utcnow()},
            "lng": {"price": 12.45, "change": "+0.23", "updated": datetime.utcnow()}
        },
        "trading_hubs": [
            "Houston, TX",
            "Dubai, UAE", 
            "Singapore",
            "London, UK",
            "Rotterdam, Netherlands",
            "Cushing, OK"
        ]
    }
    
    return mock_data

# PayPal Payment Endpoints

@app.post("/api/payments/create-subscription")
async def create_subscription_payment(
    tier: str,
    user_id: str = Depends(get_current_user)
):
    """Create PayPal subscription for premium plans"""
    if not PayPalService:
        raise HTTPException(status_code=503, detail="Payment service not available")
    
    if tier not in ["premium_basic", "premium_advanced", "enterprise"]:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Create billing plan if needed (in production, this would be done once)
    plan_id = await PayPalService.create_subscription_plan(tier)
    if not plan_id:
        raise HTTPException(status_code=500, detail="Failed to create subscription plan")
    
    # Create subscription
    result = await PayPalService.create_subscription(plan_id, user_id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create subscription")
    
    return {
        "approval_url": result["approval_url"],
        "subscription_id": result["agreement_id"],
        "payment_id": result["payment_id"]
    }

@app.post("/api/payments/create-featured-payment")
async def create_featured_payment(
    listing_type: str,
    user_id: str = Depends(get_current_user)
):
    """Create PayPal payment for featured listing"""
    if not PayPalService:
        raise HTTPException(status_code=503, detail="Payment service not available")
    
    if listing_type not in ["standard", "premium"]:
        raise HTTPException(status_code=400, detail="Invalid listing type")
    
    result = await PayPalService.create_payment(listing_type, user_id)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create payment")
    
    return {
        "approval_url": result["approval_url"],
        "payment_id": result["payment_id"],
        "internal_payment_id": result["internal_payment_id"]
    }

@app.post("/api/payments/execute")
async def execute_payment(
    payment_id: str,
    payer_id: str,
    payment_type: str = "payment"  # "payment" or "subscription"
):
    """Execute PayPal payment after user approval"""
    if payment_type == "subscription":
        success = await PayPalService.execute_agreement(payment_id)
    else:
        success = await PayPalService.execute_payment(payment_id, payer_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Payment execution failed")
    
    # Get payment details for confirmation email
    payment_details = await PayPalService.get_payment_status(payment_id)
    if payment_details and payment_details.get("status") == "completed":
        # Get user info for email
        user = users_collection.find_one({"user_id": payment_details.get("user_id")})
        if user:
            if payment_type == "subscription":
                await email_service.send_subscription_confirmation(
                    user["email"],
                    user["first_name"],
                    {
                        "tier": payment_details.get("subscription_tier", "premium"),
                        "monthly_price": payment_details.get("amount", "N/A")
                    }
                )
            else:
                await email_service.send_payment_confirmation(
                    user["email"],
                    user["first_name"],
                    payment_details
                )
    
    return {"message": "Payment executed successfully", "status": "completed"}

@app.get("/api/payments/status/{payment_id}")
async def get_payment_status(payment_id: str, user_id: str = Depends(get_current_user)):
    """Get payment status"""
    status = await PayPalService.get_payment_status(payment_id)
    if not status:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return status

@app.delete("/api/payments/cancel-subscription/{agreement_id}")
async def cancel_subscription(agreement_id: str, user_id: str = Depends(get_current_user)):
    """Cancel PayPal subscription"""
    success = await PayPalService.cancel_subscription(agreement_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to cancel subscription")
    
    return {"message": "Subscription cancelled successfully"}

@app.get("/api/payments/history")
async def get_payment_history(user_id: str = Depends(get_current_user)):
    """Get user's payment history"""
    payments = await PayPalService.get_user_payments(user_id)
    return {"payments": payments}

# Advanced Analytics Endpoints

@app.get("/api/analytics/platform")
async def get_platform_analytics(user_id: str = Depends(get_current_user)):
    """Get platform overview analytics (admin only)"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics = await analytics_service.get_platform_overview()
    return analytics

@app.get("/api/analytics/user")
async def get_user_analytics_endpoint(user_id: str = Depends(get_current_user)):
    """Get user-specific analytics"""
    if analytics_service:
        analytics = await analytics_service.get_user_analytics(user_id)
        return analytics
    else:
        # Return mock user analytics if service not available
        return {
            "user_info": {"user_id": user_id, "company_name": "Mock Company", "role": "basic"},
            "listings": {"total_listings": 0, "active_listings": 0, "featured_listings": 0, "product_breakdown": {}},
            "connections": {"connections_received": 0, "connections_made": 0, "successful_connections": 0, "connection_success_rate": 0},
            "financial": {"total_spent": 0, "payment_history": [], "subscription_status": "basic"}
        }

@app.get("/api/analytics/market")
async def get_market_analytics():
    """Get market analytics and trends"""
    if analytics_service:
        analytics = await analytics_service.get_market_analytics()
        return analytics
    else:
        # Return mock analytics data if service not available
        return {
            "product_distribution": [
                {"product_type": "crude_oil", "listing_count": 15, "avg_quantity": 50000.0},
                {"product_type": "natural_gas", "listing_count": 8, "avg_quantity": 1000.0},
                {"product_type": "lng", "listing_count": 5, "avg_quantity": 75000.0}
            ],
            "geographic_distribution": [
                {"country": "United States", "trader_count": 25, "listing_count": 12},
                {"country": "United Kingdom", "trader_count": 18, "listing_count": 8},
                {"country": "UAE", "trader_count": 15, "listing_count": 10}
            ],
            "trading_hub_activity": [
                {"hub": "Houston, TX", "listing_count": 8, "total_quantity": 400000},
                {"hub": "Dubai, UAE", "listing_count": 6, "total_quantity": 300000},
                {"hub": "Singapore", "listing_count": 4, "total_quantity": 200000}
            ],
            "price_trends": {
                "crude_oil": {"current_avg": 78.50, "weekly_change": 2.3, "monthly_change": -1.2, "volatility": "moderate"},
                "natural_gas": {"current_avg": 2.85, "weekly_change": -0.15, "monthly_change": 0.8, "volatility": "high"},
                "lng": {"current_avg": 12.45, "weekly_change": 0.95, "monthly_change": 3.2, "volatility": "low"}
            },
            "activity_trends": []
        }

@app.get("/api/analytics/revenue")
async def get_revenue_analytics(user_id: str = Depends(get_current_user)):
    """Get revenue analytics (admin only)"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    analytics = await analytics_service.get_revenue_analytics()
    return analytics

@app.get("/api/analytics/listing/{listing_id}")
async def get_listing_analytics(listing_id: str, user_id: str = Depends(get_current_user)):
    """Get analytics for a specific listing"""
    # Verify user owns the listing
    listing = listings_collection.find_one({"listing_id": listing_id, "user_id": user_id})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found or access denied")
    
    analytics = await analytics_service.get_listing_performance(listing_id)
    return analytics

# Enhanced notification endpoints

@app.post("/api/notifications/test-email")
async def test_email_notification(
    email: EmailStr,
    user_id: str = Depends(get_current_user)
):
    """Test email notification system"""
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = await email_service.send_welcome_email(email, user["first_name"])
    return {"success": success, "message": "Test email sent" if success else "Failed to send email"}

# Business Growth and User Acquisition Endpoints

@app.post("/api/referrals/create")
async def create_referral_program(
    referral_type: str = "standard",
    user_id: str = Depends(get_current_user)
):
    """Create referral program for user"""
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    result = await business_growth_service.create_referral_program(user_id, referral_type)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to create referral program")
    
    return result

@app.post("/api/referrals/signup")
async def process_referral_signup(
    referral_code: str,
    user_id: str = Depends(get_current_user)
):
    """Process new user signup through referral"""
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    result = await business_growth_service.process_referral_signup(referral_code, user_id)
    return result

@app.post("/api/referrals/convert/{user_id}")
async def process_referral_conversion(
    user_id: str,
    conversion_type: str = "subscription",
    current_user_id: str = Depends(get_current_user)
):
    """Process referral conversion (internal use)"""
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    success = await business_growth_service.process_referral_conversion(user_id, conversion_type)
    return {"success": success}

@app.get("/api/referrals/metrics")
async def get_conversion_metrics(user_id: str = Depends(get_current_user)):
    """Get user acquisition and conversion metrics"""
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    metrics = await business_growth_service.calculate_conversion_metrics()
    return metrics

@app.get("/api/acquisition/dashboard")
async def get_user_acquisition_dashboard(user_id: str = Depends(get_current_user)):
    """Get comprehensive user acquisition dashboard"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not business_growth_service:
        return {"message": "Business growth service not available"}
    
    dashboard = await business_growth_service.get_user_acquisition_dashboard()
    return dashboard

# Content Marketing and SEO Endpoints

@app.post("/api/content/article")
async def create_market_insight_article(
    title: str,
    content: str,
    category: str,
    user_id: str = Depends(get_current_user)
):
    """Create market insight article for thought leadership"""
    if not content_marketing_service:
        raise HTTPException(status_code=503, detail="Content marketing service not available")
    
    article = await content_marketing_service.create_market_insight_article(title, content, category, user_id)
    if not article:
        raise HTTPException(status_code=500, detail="Failed to create article")
    
    return article

@app.post("/api/content/market-report")
async def generate_weekly_market_report(user_id: str = Depends(get_current_user)):
    """Generate comprehensive weekly market report"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not content_marketing_service:
        raise HTTPException(status_code=503, detail="Content marketing service not available")
    
    report = await content_marketing_service.generate_weekly_market_report()
    return report

@app.post("/api/content/seo-content")
async def create_seo_content(
    topic: str,
    target_keywords: List[str],
    content_type: str = "article",
    user_id: str = Depends(get_current_user)
):
    """Create SEO-optimized content for organic traffic"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not content_marketing_service:
        raise HTTPException(status_code=503, detail="Content marketing service not available")
    
    content = await content_marketing_service.create_seo_optimized_content(topic, target_keywords, content_type)
    return content

@app.post("/api/content/whitepaper")
async def generate_industry_whitepaper(
    title: str,
    research_topic: str,
    user_id: str = Depends(get_current_user)
):
    """Generate comprehensive industry whitepapers for lead generation"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not content_marketing_service:
        raise HTTPException(status_code=503, detail="Content marketing service not available")
    
    whitepaper = await content_marketing_service.generate_industry_whitepaper(title, research_topic)
    return whitepaper

@app.get("/api/content/performance")
async def get_content_performance(user_id: str = Depends(get_current_user)):
    """Get content marketing performance and ROI"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not content_marketing_service:
        return {"message": "Content marketing service not available"}
    
    performance = await content_marketing_service.track_content_performance()
    return performance

@app.get("/api/content/dashboard")
async def get_content_marketing_dashboard(user_id: str = Depends(get_current_user)):
    """Get comprehensive content marketing dashboard"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not content_marketing_service:
        return {"message": "Content marketing service not available"}
    
    dashboard = await content_marketing_service.get_content_marketing_dashboard()
    return dashboard

# Lead Generation Endpoints

@app.post("/api/leads/magnet")
async def create_lead_magnet(
    title: str,
    content_type: str,
    target_audience: str,
    user_id: str = Depends(get_current_user)
):
    """Create lead magnets for user acquisition"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    lead_magnet = await business_growth_service.create_lead_magnet(title, content_type, target_audience)
    return lead_magnet

@app.post("/api/leads/track")
async def track_lead_generation(
    lead_magnet_id: str,
    user_email: EmailStr,
    source: str = "organic"
):
    """Track lead generation from lead magnets"""
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    success = await business_growth_service.track_lead_generation(lead_magnet_id, user_email, source)
    return {"success": success}

# Partnership and Affiliate Program Endpoints

@app.post("/api/partnerships/create")
async def create_partnership_program(
    partner_type: str,
    commission_rate: float,
    user_id: str = Depends(get_current_user)
):
    """Create partnership and affiliate programs"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if not business_growth_service:
        raise HTTPException(status_code=503, detail="Business growth service not available")
    
    program = await business_growth_service.create_partnership_program(partner_type, commission_rate)
    return program

# Enhanced market data with business intelligence

@app.get("/api/market-intelligence")
async def get_market_intelligence():
    """Get comprehensive market intelligence and business insights"""
    # Enhanced market data with business insights
    intelligence = {
        "market_overview": {
            "oil_markets": {
                "wti_crude": {"price": 78.45, "trend": "bullish", "support": 75.00, "resistance": 82.00},
                "brent_crude": {"price": 82.15, "trend": "bullish", "support": 79.00, "resistance": 85.00},
                "dubai_crude": {"price": 81.23, "trend": "neutral", "support": 78.00, "resistance": 84.00}
            },
            "gas_markets": {
                "natural_gas": {"price": 2.85, "trend": "bearish", "support": 2.70, "resistance": 3.00},
                "lng_asia": {"price": 12.45, "trend": "bullish", "support": 11.50, "resistance": 13.50}
            }
        },
        "trading_opportunities": [
            {
                "market": "WTI Crude",
                "opportunity": "Bullish breakout above $80",
                "risk_reward": "1:3",
                "time_horizon": "2-4 weeks",
                "confidence": "High"
            },
            {
                "market": "Natural Gas",
                "opportunity": "Seasonal winter demand support",
                "risk_reward": "1:2",
                "time_horizon": "1-3 months",
                "confidence": "Medium"
            }
        ],
        "risk_factors": [
            "OPEC+ production policy changes",
            "US Federal Reserve interest rate decisions",
            "Geopolitical tensions in Middle East",
            "Winter weather patterns in Northern Hemisphere"
        ],
        "industry_insights": {
            "supply_demand": "Tight supply conditions support oil prices",
            "inventory_levels": "Below 5-year average for crude oil",
            "refining_margins": "Strong crack spreads indicate healthy demand",
            "transportation": "Shipping costs elevated due to supply chain issues"
        },
        "weekly_outlook": {
            "key_events": [
                "EIA Weekly Petroleum Status Report (Wednesday)",
                "OPEC+ Technical Committee Meeting",
                "Chinese economic data release",
                "US inflation data (CPI)"
            ],
            "price_targets": {
                "wti_crude": {"bull_target": 85.00, "bear_target": 72.00},
                "natural_gas": {"bull_target": 3.20, "bear_target": 2.50}
            }
        }
    }
    
    return intelligence

@app.post("/api/payments/webhook")
async def paypal_webhook(request: Request):
    """Handle PayPal webhook notifications"""
    try:
        from paypal_webhook_handler import paypal_webhook_handler
        result = await paypal_webhook_handler.handle_webhook(request)
        return result
    except Exception as e:
        print(f"Webhook processing error: {str(e)}")
        return {"status": "error", "message": "Webhook processing failed"}

@app.get("/api/payments/revenue-dashboard")
async def get_revenue_dashboard(user_id: str = Depends(get_current_user)):
    """Get real-time revenue dashboard"""
    user = users_collection.find_one({"user_id": user_id})
    if not user or user.get("role") not in ["enterprise", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Calculate real revenue metrics
    total_revenue = sum([p.get("amount", 0) for p in db.payments.find({"status": "completed"})])
    active_subscriptions = db.payments.count_documents({"payment_type": "subscription", "status": "active"})
    monthly_recurring_revenue = sum([p.get("amount", 0) for p in db.payments.find({
        "payment_type": "subscription", 
        "status": "active"
    })])
    
    # Featured listing revenue
    listing_revenue = sum([p.get("amount", 0) for p in db.payments.find({
        "payment_type": "featured_listing", 
        "status": "completed"
    })])
    
    # This month's revenue
    current_month = datetime.utcnow().strftime("%Y-%m")
    monthly_revenue = sum([p.get("amount", 0) for p in db.subscription_payments.find({
        "billing_cycle": current_month
    })])
    
    return {
        "total_revenue": total_revenue,
        "monthly_recurring_revenue": monthly_recurring_revenue,
        "active_subscriptions": active_subscriptions,
        "listing_revenue": listing_revenue,
        "current_month_revenue": monthly_revenue,
        "projected_annual_revenue": monthly_recurring_revenue * 12,
        "average_revenue_per_user": total_revenue / max(users_collection.count_documents({}), 1),
        "revenue_growth_rate": 23.5,  # Mock growth rate
        "last_updated": datetime.utcnow()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
