from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request
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

# Import our new services
from paypal_service import PayPalService
from email_service import email_service
from analytics_service import analytics_service

# Initialize FastAPI app
app = FastAPI(title="Oil & Gas Finder API", version="1.0.0")

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
    await email_service.send_welcome_email(user_data.email, user_data.first_name)
    
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
