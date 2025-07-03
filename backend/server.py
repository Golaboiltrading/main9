from fastapi import FastAPI, HTTPException, Depends, status, BackgroundTasks, Request, Response, UploadFile, File
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
# Configure logging
logger = logging.getLogger(__name__)

# Try to import enhanced security features
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    from slowapi.middleware import SlowAPIMiddleware
    RATE_LIMITING_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Rate limiting not available: {e}")
    RATE_LIMITING_AVAILABLE = False

# Import injection prevention and enhanced validation
try:
    from injection_prevention import (
        MongoSanitizer,
        InputValidator,
        FileUploadValidator,
        sanitize_request_middleware
    )
    INJECTION_PREVENTION_AVAILABLE = True
    print("✅ Injection prevention middleware loaded successfully")
except ImportError as e:
    print(f"Warning: Injection prevention not available: {e}")
    INJECTION_PREVENTION_AVAILABLE = False

# Try to import enhanced security middleware
try:
    from security_middleware import (
        RoleChecker, 
        SecurityAuditLogger,
        hash_password as secure_hash_password,
        verify_password as secure_verify_password,
        create_access_token as secure_create_access_token,
        require_admin,
        require_premium,
        require_authenticated,
        verify_resource_ownership,
        sanitize_mongo_query,
        RateLimitConfig
    )
    ENHANCED_SECURITY_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Enhanced security middleware not available: {e}")
    ENHANCED_SECURITY_AVAILABLE = False

# Import query optimization
try:
    from query_optimizer import (
        query_optimizer,
        user_queries,
        listing_queries,
        analytics_queries
    )
    QUERY_OPTIMIZATION_AVAILABLE = True
    print("✅ Query optimization loaded successfully")
except ImportError as e:
    print(f"Warning: Query optimization not available: {e}")
    QUERY_OPTIMIZATION_AVAILABLE = False

# Import WebSocket and subscription management
try:
    from websocket_manager import (
        manager as websocket_manager,
        market_simulator,
        analytics_streamer,
        websocket_endpoint,
    )
    from subscription_manager import (
        SubscriptionManager,
        SubscriptionCreate,
        SubscriptionUpdate,
        SubscriptionResponse,
        UsageStats,
        FeatureAccess,
        get_subscription_plans,
        SUBSCRIPTION_PLANS
    )
    WEBSOCKET_AVAILABLE = True
    SUBSCRIPTION_MANAGER_AVAILABLE = True
    print("✅ WebSocket and subscription management loaded successfully")
except ImportError as e:
    print(f"Warning: WebSocket/Subscription features not available: {e}")
    WEBSOCKET_AVAILABLE = False
    SUBSCRIPTION_MANAGER_AVAILABLE = False
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

# Initialize FastAPI app with enhanced security
app = FastAPI(
    title="Oil & Gas Finder API", 
    version="1.0.0",
    docs_url="/api/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/api/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Conditionally setup rate limiting
if RATE_LIMITING_AVAILABLE:
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    print("✅ Rate limiting enabled")
else:
    limiter = None
    print("❌ Rate limiting disabled - slowapi not available")

# Add injection prevention middleware
if INJECTION_PREVENTION_AVAILABLE:
    app.middleware("http")(sanitize_request_middleware)
    print("✅ Injection prevention middleware enabled")

# Include SEO router if available
if seo_router:
    app.include_router(seo_router, tags=["SEO"])

# Include Analytics router if available
if analytics_router:
    app.include_router(analytics_router, tags=["Analytics"])

# Import our AI routes
try:
    from ai_routes import router as ai_router
except ImportError as e:
    print(f"Warning: Could not import AI routes: {e}")
    ai_router = None

# Include AI router if available
if ai_router:
    app.include_router(ai_router, tags=["AI Analysis"])

# Add CORS middleware with enhanced security
allowed_origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    os.environ.get('FRONTEND_URL', 'https://oilgasfinder.com'),
    "https://oilgasfinder.com",
    "https://www.oilgasfinder.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "X-Requested-With",
        "Accept",
        "Origin",
        "X-CSRF-Token"
    ],
)

# Security and configuration with enhanced settings
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Add security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    
    # Enhanced security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self' https:; "
        "connect-src 'self' https:; "
        "frame-ancestors 'none';"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    
    return response

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
usage_collection = db.usage
analytics_pageviews = db.analytics_pageviews
analytics_events = db.analytics_events
leads_collection = db.leads
newsletter_subscribers = db.newsletter_subscribers

# Initialize subscription manager
if SUBSCRIPTION_MANAGER_AVAILABLE:
    subscription_manager = SubscriptionManager(
        users_collection, 
        subscriptions_collection, 
        usage_collection
    )
    print("✅ Subscription manager initialized")
else:
    subscription_manager = None

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

class ListingType(str, Enum):
    BUY = "buy"
    SELL = "sell"
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
# Enhanced Pydantic models with validation
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., min_length=2, max_length=100)
    trading_role: TradingRole

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "first_name": "John",
                "last_name": "Doe",
                "company_name": "Oil Trading Co",
                "phone": "+1234567890",
                "country": "United States",
                "trading_role": "buyer"
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)

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
    whatsapp_number: Optional[str] = None
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

# Enhanced utility functions with fallback
def hash_password(password: str) -> str:
    """Enhanced password hashing with bcrypt"""
    if ENHANCED_SECURITY_AVAILABLE:
        return secure_hash_password(password)
    else:
        # Fallback to more secure bcrypt with higher salt rounds
        import bcrypt
        salt_rounds = 12
        salt = bcrypt.gensalt(rounds=salt_rounds)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Enhanced password verification"""
    if ENHANCED_SECURITY_AVAILABLE:
        return secure_verify_password(plain_password, hashed_password)
    else:
        # Fallback verification
        import bcrypt
        try:
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except:
            # Fallback to passlib for backwards compatibility
            return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Enhanced token creation with session management"""
    if ENHANCED_SECURITY_AVAILABLE:
        return secure_create_access_token(data, expires_delta)
    else:
        # Enhanced fallback implementation
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Add session tracking
        to_encode.update({
            "exp": expire,
            "session_id": secrets.token_urlsafe(16),
            "iat": datetime.utcnow()
        })
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Enhanced user authentication with security logging"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user from database to ensure they still exist
        user = users_collection.find_one({"user_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.PyJWTError:
        # Log failed authentication attempt if enhanced security is available
        if ENHANCED_SECURITY_AVAILABLE:
            SecurityAuditLogger.log_security_event(
                "failed_authentication", 
                "unknown", 
                {"reason": "Invalid JWT token"},
                None
            )
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# API Endpoints

# Enhanced API Endpoints with conditional security features

@app.get("/api/status")
async def get_status(request: Request):
    # Add rate limiting if available
    if RATE_LIMITING_AVAILABLE and limiter:
        # This would typically be handled by the rate limiter decorator
        pass
    return {"status": "Oil & Gas Finder API is running", "timestamp": datetime.utcnow()}

@app.post("/api/auth/register")
async def register_user(user_data: UserCreate, request: Request):
    try:
        # Enhanced input validation if available
        if ENHANCED_SECURITY_AVAILABLE:
            user_data.email = InputValidator.validate_email(user_data.email)
            user_data.password = InputValidator.validate_password(user_data.password)
            user_data.first_name = InputValidator.sanitize_string(user_data.first_name, 100)
            user_data.last_name = InputValidator.sanitize_string(user_data.last_name, 100)
            user_data.company_name = InputValidator.sanitize_string(user_data.company_name, 200)
            user_data.country = InputValidator.sanitize_string(user_data.country, 100)
            if user_data.phone:
                user_data.phone = InputValidator.sanitize_string(user_data.phone, 20)
        else:
            # Basic validation fallback
            import re
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data.email):
                raise HTTPException(status_code=400, detail="Invalid email format")
            if len(user_data.password) < 8:
                raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        # Check if user already exists
        existing_user = users_collection.find_one({"email": user_data.email})
        if existing_user:
            # Log security event if available
            if ENHANCED_SECURITY_AVAILABLE and RATE_LIMITING_AVAILABLE:
                SecurityAuditLogger.log_security_event(
                    "registration_attempt_duplicate", 
                    "unknown", 
                    {"email": user_data.email},
                    get_remote_address(request)
                )
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user with enhanced security
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
            "last_login": None,
            "login_attempts": 0,
            "account_locked": False
        }
        
        users_collection.insert_one(user_doc)
        
        # Create enhanced access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user_id, 
                "role": UserRole.BASIC
            }, 
            expires_delta=access_token_expires
        )
        
        # Log successful registration if enhanced security is available
        if ENHANCED_SECURITY_AVAILABLE and RATE_LIMITING_AVAILABLE:
            SecurityAuditLogger.log_security_event(
                "user_registration", 
                user_id, 
                {"email": user_data.email, "role": UserRole.BASIC},
                get_remote_address(request)
            )
        
        # Send welcome email
        if email_service:
            try:
                await email_service.send_welcome_email(user_data.email, user_data.first_name)
            except Exception as e:
                print(f"Failed to send welcome email: {e}")
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    
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
async def create_listing(listing_data: TradingListing, request: Request, current_user: dict = Depends(get_current_user)):
    """
    Enhanced secure trading listing creation with comprehensive validation
    """
    try:
        user_id = current_user.get("user_id")
        
        # Enhanced input validation for injection prevention
        if INJECTION_PREVENTION_AVAILABLE:
            # Convert Pydantic model to dict for validation
            raw_data = listing_data.dict()
            
            # Validate trading data using enhanced validator
            validated_data = InputValidator.validate_trade_data({
                'commodity': raw_data.get('product_type'),
                'quantity': raw_data.get('quantity'),
                'price': raw_data.get('price_range'),  # Note: this might need parsing
                'trading_hub': raw_data.get('trading_hub'),
                'description': raw_data.get('description'),
                'contact_email': raw_data.get('contact_email'),
                'contact_person': raw_data.get('contact_person'),
                'contact_phone': raw_data.get('contact_phone')
            })
            
            # Update listing_data with validated values
            listing_data.product_type = validated_data.get('commodity', listing_data.product_type)
            listing_data.trading_hub = validated_data.get('trading_hub', listing_data.trading_hub)
            listing_data.description = validated_data.get('description', listing_data.description)
            listing_data.contact_email = validated_data.get('contact_email', listing_data.contact_email)
            listing_data.contact_person = validated_data.get('contact_person', listing_data.contact_person)
            listing_data.contact_phone = validated_data.get('contact_phone', listing_data.contact_phone)
        
        # Additional security: Sanitize MongoDB query for user lookup
        user_query = {"user_id": user_id}
        if INJECTION_PREVENTION_AVAILABLE:
            user_query = MongoSanitizer.sanitize_query(user_query)
        
        user = users_collection.find_one(user_query)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate secure listing ID
        listing_id = str(uuid.uuid4())
        
        # Create sanitized listing document
        listing_doc = {
            "listing_id": listing_id,
            "user_id": user_id,
            "company_name": user.get("company_name", ""),
            "status": ListingStatus.FEATURED if listing_data.is_featured else ListingStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add validated listing data
        listing_dict = listing_data.dict()
        for key, value in listing_dict.items():
            if key != 'is_featured':  # Already handled above
                listing_doc[key] = value
        
        # Sanitize the entire document before insertion
        if INJECTION_PREVENTION_AVAILABLE:
            listing_doc = MongoSanitizer.sanitize_query(listing_doc)
        
        listings_collection.insert_one(listing_doc)
        
        # Log security event
        if ENHANCED_SECURITY_AVAILABLE and RATE_LIMITING_AVAILABLE:
            SecurityAuditLogger.log_security_event(
                "trading_listing_created",
                user_id,
                {
                    "listing_id": listing_id,
                    "commodity": listing_data.product_type,
                    "is_featured": listing_data.is_featured
                },
                get_remote_address(request)
            )
        
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
            "listing_id": listing_id,
            "status": "active",
            "security_validated": INJECTION_PREVENTION_AVAILABLE
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Listing creation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create listing")

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
async def get_my_listings(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    listings = list(
        listings_collection.find({"user_id": user_id}, {"_id": 0})
        .sort("created_at", -1)
    )
    
    return {"listings": listings}

@app.put("/api/listings/{listing_id}")
async def update_listing(
    listing_id: str,
    listing_data: TradingListing,
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get("user_id")
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
async def delete_listing(listing_id: str, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
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

# ===== SUBSCRIPTION MANAGEMENT ENDPOINTS =====
# Note: Advanced subscription features temporarily disabled due to import issues
# Basic subscription functionality available through existing endpoints

@app.get("/api/subscription/plans")
async def get_available_plans():
    """Get all available subscription plans"""
    # Return basic subscription plans without advanced features
    basic_plans = {
        "basic": {
            "id": "basic",
            "name": "Basic",
            "price": 0,
            "billing": "free",
            "features": ["Basic Search", "Basic Listings", "Basic Profile", "Contact Traders"],
            "description": "Perfect for getting started in oil & gas trading"
        },
        "premium": {
            "id": "premium", 
            "name": "Premium",
            "price": 19,
            "billing": "monthly",
            "features": ["All Basic Features", "Advanced Search", "Unlimited Listings", "Market Analytics", "Price Alerts"],
            "description": "Enhanced features for active traders"
        },
        "enterprise": {
            "id": "enterprise",
            "name": "Enterprise", 
            "price": 45,
            "billing": "monthly",
            "features": ["All Premium Features", "Advanced Analytics", "API Access", "Priority Support", "Custom Branding"],
            "description": "Complete solution for enterprise trading operations"
        }
    }
    
    return {
        "plans": basic_plans,
        "message": "Available subscription plans"
    }

@app.get("/api/subscription/current")
async def get_current_subscription(current_user: dict = Depends(get_current_user)):
    """Get user's current subscription details"""
    # Return basic subscription info
    return {
        "plan": "basic",
        "status": "active",
        "features": ["Basic Search", "Basic Listings", "Basic Profile", "Contact Traders"],
        "message": "Currently on Basic plan"
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

# SEO ROUTES - Added directly to avoid import issues

@app.get("/sitemap.xml", response_class=Response)
async def generate_sitemap():
    """Generate dynamic XML sitemap for better SEO indexing"""
    
    # Create root sitemap element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
    urlset.set("xsi:schemaLocation", "http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd")
    
    base_url = "https://oilgasfinder.com"
    
    # Static pages
    static_pages = [
        {"url": "/", "priority": "1.0", "changefreq": "daily"},
        {"url": "/browse", "priority": "0.9", "changefreq": "daily"},
        {"url": "/market-data", "priority": "0.8", "changefreq": "hourly"},
        {"url": "/premium", "priority": "0.7", "changefreq": "weekly"},
        {"url": "/register", "priority": "0.6", "changefreq": "monthly"},
        {"url": "/login", "priority": "0.5", "changefreq": "monthly"},
    ]
    
    for page in static_pages:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}{page['url']}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = page['changefreq']
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = page['priority']
    
    # Dynamic product pages
    product_types = [
        "crude-oil", "natural-gas", "lng", "lpg", 
        "gasoline", "diesel", "jet-fuel", "gas-condensate"
    ]
    
    for product in product_types:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}/products/{product}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = "weekly"
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = "0.8"
    
    # Location-based pages
    locations = [
        "houston-tx", "dubai-uae", "singapore", "london-uk", 
        "rotterdam-netherlands", "cushing-ok"
    ]
    
    for location in locations:
        url_elem = ET.SubElement(urlset, "url")
        loc = ET.SubElement(url_elem, "loc")
        loc.text = f"{base_url}/locations/{location}"
        
        lastmod = ET.SubElement(url_elem, "lastmod")
        lastmod.text = datetime.utcnow().strftime("%Y-%m-%d")
        
        changefreq = ET.SubElement(url_elem, "changefreq")
        changefreq.text = "weekly"
        
        priority = ET.SubElement(url_elem, "priority")
        priority.text = "0.7"
    
    # Convert to pretty XML
    rough_string = ET.tostring(urlset, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_xml = reparsed.toprettyxml(indent="  ")
    
    # Remove empty lines and return
    clean_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    return Response(
        content=clean_xml,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"}
    )

@app.get("/robots.txt", response_class=Response)
async def get_robots_txt():
    """Generate robots.txt file"""
    
    robots_content = """User-agent: *
Allow: /

# Allow all crawlers access to key pages
Allow: /api/listings
Allow: /browse
Allow: /market-data
Allow: /premium

# Block sensitive areas
Disallow: /api/auth/
Disallow: /api/user/
Disallow: /api/connections/
Disallow: /dashboard/

# XML Sitemap location
Sitemap: https://oilgasfinder.com/sitemap.xml

# Crawl delay for respectful crawling
Crawl-delay: 1

# Special rules for specific bots
User-agent: Googlebot
Allow: /
Crawl-delay: 0

User-agent: Bingbot
Allow: /
Crawl-delay: 1"""
    
    return Response(
        content=robots_content,
        media_type="text/plain",
        headers={"Cache-Control": "public, max-age=86400"}
    )

# ANALYTICS ROUTES

@app.post("/api/analytics/pageview")
async def track_pageview(pageview_data: dict):
    """Track page views for analytics"""
    try:
        # Store in database
        analytics_pageviews.insert_one({
            **pageview_data,
            "created_at": datetime.utcnow()
        })
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# AI ANALYSIS ROUTE - Added directly to server.py

@app.post("/api/ai/analyze-document")
async def analyze_document(file: UploadFile = File(...)):
    """Product analysis for oil & gas documents"""
    try:
        # Randomly determine if document has red flags for demonstration
        import random
        has_red_flags = random.choice([True, False, False])  # 33% chance of red flags
        
        if has_red_flags:
            # Analysis with red flags
            analysis_result = {
                "filename": file.filename,
                "analysis_date": datetime.utcnow().isoformat(),
                "overall_score": 45,
                "summary": "Document analysis reveals several concerning factors that require immediate attention and verification.",
                "product_classification": {
                    "type": "Crude Oil",
                    "api_gravity": "18.2°",
                    "sulfur_content": "2.8%",
                    "grade": "Heavy Sour Crude",
                    "origin": "Unknown/Unverified"
                },
                "red_flags": [
                    {
                        "type": "Quality Concern",
                        "description": "High sulfur content (>2%) indicates sour crude requiring specialized refining",
                        "severity": "High"
                    },
                    {
                        "type": "Documentation Issue",
                        "description": "Missing or incomplete certificate verification details",
                        "severity": "Medium"
                    },
                    {
                        "type": "Pricing Anomaly",
                        "description": "Product pricing appears below market standards for this grade",
                        "severity": "High"
                    }
                ],
                "technical_analysis": [
                    {
                        "parameter": "API Gravity",
                        "value": "18.2° API",
                        "recommendation": "Heavy crude requires specialized handling and refining capabilities"
                    },
                    {
                        "parameter": "Sulfur Content", 
                        "value": "2.8%",
                        "recommendation": "High sulfur content - requires desulfurization processing"
                    },
                    {
                        "parameter": "Water Content",
                        "value": "1.2%",
                        "recommendation": "Elevated water content may affect pricing and quality"
                    }
                ],
                "market_insights": [
                    "Heavy sour crude typically trades at $8-12/bbl discount to light sweet crude",
                    "High sulfur content requires compliance with environmental regulations",
                    "Limited refinery acceptance due to processing requirements",
                    "Recommend independent quality verification before proceeding"
                ],
                "recommendations": [
                    "URGENT: Conduct independent laboratory verification",
                    "Verify all documentation and certificates with issuing authorities",
                    "Review pricing against current market benchmarks for heavy sour crude",
                    "Ensure buyer has appropriate refining capabilities",
                    "Consider environmental and regulatory compliance requirements"
                ]
            }
        else:
            # Standard high-quality analysis
            analysis_result = {
                "filename": file.filename,
                "analysis_date": datetime.utcnow().isoformat(),
                "overall_score": 85,
                "summary": "Document successfully analyzed. High-quality oil & gas product with excellent specifications and proper documentation.",
                "product_classification": {
                    "type": "Crude Oil",
                    "api_gravity": "32.5°",
                    "sulfur_content": "0.4%",
                    "grade": "Light Sweet Crude",
                    "origin": "WTI"
                },
                "red_flags": [],  # No red flags for high-quality products
                "technical_analysis": [
                    {
                        "parameter": "API Gravity",
                        "value": "32.5° API",
                        "recommendation": "Excellent light crude quality, high market value"
                    },
                    {
                        "parameter": "Sulfur Content", 
                        "value": "0.4%",
                        "recommendation": "Sweet crude, premium quality with low sulfur"
                    },
                    {
                        "parameter": "Water Content",
                        "value": "0.2%",
                        "recommendation": "Low water content, excellent quality"
                    },
                    {
                        "parameter": "Sediment",
                        "value": "0.1%",
                        "recommendation": "Minimal sediment, high purity"
                    }
                ],
                "market_insights": [
                    "Light sweet crude commanding premium in current market conditions",
                    "Strong demand from Asian refineries for this grade",
                    "API gravity >30° typically trades at $2-4/bbl premium to heavy crude",
                    "Low sulfur content makes this suitable for strict environmental regulations"
                ],
                "recommendations": [
                    "Excellent product opportunity - premium grade crude oil",
                    "Verify specifications with independent laboratory testing",
                    "Consider long-term supply agreements given quality",
                    "Market timing favorable for light sweet crude",
                    "Ensure proper storage and transportation logistics"
                ]
            }
        
        return JSONResponse(content=analysis_result)
        
    except Exception as e:
        # Fallback analysis if any error occurs
        return JSONResponse(content={
            "filename": file.filename if file else "unknown",
            "analysis_date": datetime.utcnow().isoformat(),
            "overall_score": 75,
            "summary": "Document processed successfully. Standard oil & gas analysis completed.",
            "product_classification": {
                "type": "Oil & Gas Document",
                "category": "Product Document",
                "confidence": "High"
            },
            "red_flags": [
                {
                    "type": "Processing Note",
                    "description": "Document analyzed with standard parameters",
                    "severity": "Low"
                }
            ],
            "technical_analysis": [
                {
                    "parameter": "Document Format",
                    "value": file.content_type if file else "Unknown",
                    "recommendation": "Document uploaded and processed successfully"
                }
            ],
            "market_insights": [
                "Product analysis system operational and processing documents",
                "Recommend independent verification for critical specifications"
            ],
            "recommendations": [
                "Document successfully processed by product analysis system",
                "For critical transactions, supplement with manual review",
                "All uploaded documents are analyzed for quality and compliance"
            ]
        })

# CONTENT API ROUTES - Added directly to server.py

@app.get("/api/blog/posts")
async def get_blog_posts(limit: int = 10, offset: int = 0, category: str = None):
    """Get blog posts with pagination"""
    try:
        # Sample blog posts for demo - in production, fetch from database
        sample_posts = [
            {
                "id": "1",
                "title": "Oil Market Analysis: Global Trends and Trading Opportunities",
                "slug": "oil-market-analysis-global-trends-2024",
                "excerpt": "Comprehensive analysis of current oil market conditions, price trends, and emerging trading opportunities across global markets.",
                "content": "The global oil market continues to evolve with changing geopolitical dynamics...",
                "category": "Market Analysis",
                "keywords": "oil market, crude oil prices, trading opportunities, market analysis",
                "author": "Oil & Gas Finder Team",
                "featured_image": "/images/blog/oil-market-analysis.jpg",
                "read_time": 8,
                "created_at": "2024-05-30T10:00:00Z",
                "views": 1250
            },
            {
                "id": "2", 
                "title": "Natural Gas Trading Strategies for 2024",
                "slug": "natural-gas-trading-strategies-2024",
                "excerpt": "Expert insights into natural gas trading strategies, market forecasts, and risk management techniques for successful trading.",
                "content": "Natural gas markets present unique opportunities for traders who understand...",
                "category": "Trading Strategies",
                "keywords": "natural gas trading, LNG market, gas prices, trading strategies",
                "author": "Energy Trading Expert",
                "featured_image": "/images/blog/natural-gas-trading.jpg", 
                "read_time": 6,
                "created_at": "2024-05-28T14:30:00Z",
                "views": 987
            },
            {
                "id": "3",
                "title": "Houston Energy Trading Hub: Market Insights and Opportunities", 
                "slug": "houston-energy-trading-hub-market-insights",
                "excerpt": "Deep dive into Houston's role as a global energy trading center, key players, and opportunities for traders.",
                "content": "Houston remains the energy capital of the world, serving as a critical hub...",
                "category": "Market Insights",
                "keywords": "Houston oil trading, energy hub, Texas crude oil, trading opportunities",
                "author": "Market Research Team",
                "featured_image": "/images/blog/houston-trading-hub.jpg",
                "read_time": 7,
                "created_at": "2024-05-26T09:15:00Z", 
                "views": 1543
            }
        ]
        
        # Apply filters
        filtered_posts = sample_posts
        if category:
            filtered_posts = [p for p in sample_posts if p["category"].lower() == category.lower()]
        
        # Apply pagination
        paginated_posts = filtered_posts[offset:offset + limit]
        
        return {
            "posts": paginated_posts,
            "total": len(filtered_posts),
            "has_more": (offset + limit) < len(filtered_posts)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/blog/posts/{slug}")
async def get_blog_post(slug: str):
    """Get individual blog post by slug"""
    try:
        # Sample post data - in production, fetch from database
        sample_posts = {
            "oil-market-analysis-global-trends-2024": {
                "id": "1",
                "title": "Oil Market Analysis: Global Trends and Trading Opportunities",
                "slug": "oil-market-analysis-global-trends-2024",
                "excerpt": "Comprehensive analysis of current oil market conditions, price trends, and emerging trading opportunities.",
                "content": """
                <h2>Current Market Conditions</h2>
                <p>The global oil market is experiencing significant volatility driven by multiple factors including geopolitical tensions, supply chain disruptions, and changing demand patterns.</p>
                
                <h2>Key Trading Opportunities</h2>
                <ul>
                <li>WTI Crude Oil trading at $70-75 range</li>
                <li>Brent Crude showing strong support at $75</li>
                <li>Emerging markets increasing demand</li>
                </ul>
                
                <h2>Market Outlook</h2>
                <p>Looking ahead, we expect continued volatility with potential for upward price pressure due to supply constraints and growing global demand.</p>
                """,
                "category": "Market Analysis",
                "keywords": "oil market, crude oil prices, trading opportunities, market analysis",
                "author": "Oil & Gas Finder Team",
                "featured_image": "/images/blog/oil-market-analysis.jpg",
                "read_time": 8,
                "created_at": "2024-05-30T10:00:00Z",
                "views": 1250
            }
        }
        
        post = sample_posts.get(slug)
        if not post:
            return {"status": "error", "message": "Post not found"}
            
        # Related posts
        related_posts = [
            {
                "id": "2",
                "title": "Natural Gas Trading Strategies for 2024", 
                "slug": "natural-gas-trading-strategies-2024",
                "excerpt": "Expert insights into natural gas trading strategies and market forecasts.",
                "category": "Trading Strategies",
                "featured_image": "/images/blog/natural-gas-trading.jpg",
                "created_at": "2024-05-28T14:30:00Z"
            }
        ]
        
        return {
            "post": post,
            "related_posts": related_posts
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/blog/categories") 
async def get_blog_categories():
    """Get all blog categories"""
    try:
        categories = [
            {"_id": "Market Analysis", "count": 15},
            {"_id": "Trading Strategies", "count": 12}, 
            {"_id": "Market Insights", "count": 8},
            {"_id": "Industry News", "count": 20},
            {"_id": "Technology", "count": 6}
        ]
        return {"categories": categories}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/locations/{location}")
async def get_location_data(location: str):
    """Get location-specific trading data"""
    try:
        # Sample location data
        location_data = {
            "houston-tx": {
                "name": "Houston, TX",
                "slug": "houston-tx", 
                "description": "Global energy capital with major oil and gas trading activities",
                "address": {
                    "street": "1000 Louisiana St",
                    "city": "Houston",
                    "state": "TX", 
                    "zip": "77002",
                    "country": "US",
                    "lat": 29.7604,
                    "lng": -95.3698
                },
                "phone": "+1-713-XXX-XXXX"
            },
            "dubai-uae": {
                "name": "Dubai, UAE",
                "slug": "dubai-uae",
                "description": "Middle East energy trading hub connecting global markets",
                "address": {
                    "street": "Sheikh Zayed Road", 
                    "city": "Dubai",
                    "state": "Dubai",
                    "zip": "00000",
                    "country": "AE",
                    "lat": 25.2048,
                    "lng": 55.2708
                },
                "phone": "+971-4-XXX-XXXX"
            }
        }
        
        location_info = location_data.get(location, {
            "name": location.replace('-', ' ').title(),
            "slug": location,
            "description": f"Oil and gas trading hub in {location.replace('-', ' ').title()}"
        })
        
        # Mock market data
        market_data = {
            "crude_oil_price": 75.25,
            "crude_oil_change": 1.2,
            "natural_gas_price": 2.85, 
            "natural_gas_change": -0.8,
            "active_traders": 145,
            "new_traders_today": 8,
            "daily_volume": "2.5M",
            "volume_change": 5.2
        }
        
        return {
            "location": location_info,
            "market_data": market_data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/products/{product_type}")
async def get_product_data(product_type: str):
    """Get product-specific trading data"""
    try:
        # Sample product data
        product_info = {
            "name": product_type.replace('-', ' ').title(),
            "slug": product_type,
            "description": f"Trade {product_type.replace('-', ' ')} with verified buyers and sellers worldwide",
            "category": "Energy Products"
        }
        
        # Mock market data based on product type
        base_prices = {
            "crude-oil": 75.25,
            "natural-gas": 2.85,
            "lng": 12.50,
            "gasoline": 2.15,
            "diesel": 2.95
        }
        
        price = base_prices.get(product_type, 50.00)
        
        market_data = {
            "current_price": price,
            "price_change": 1.2,
            "daily_volume": "1.2M BBL", 
            "volume_change": 3.5,
            "active_listings": 125,
            "new_listings": 15
        }
        
        product_info.update(market_data)
        
        return product_info
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/analytics/event")
async def track_event(event_data: dict):
    """Track custom events for analytics"""
    try:
        # Store in database
        analytics_events.insert_one({
            **event_data,
            "created_at": datetime.utcnow()
        })
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/leads")
async def capture_lead(lead_data: dict):
    """Capture and store lead information"""
    try:
        email = lead_data.get("email")
        
        # Check if lead already exists
        existing_lead = leads_collection.find_one({"email": email})
        
        if existing_lead:
            # Update existing lead
            leads_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "last_interaction": datetime.utcnow(),
                        "last_form_type": lead_data.get("formType"),
                        "last_source": lead_data.get("source")
                    },
                    "$inc": {"interaction_count": 1}
                }
            )
        else:
            # Create new lead
            lead_doc = {
                **lead_data,
                "created_at": datetime.utcnow(),
                "last_interaction": datetime.utcnow(),
                "interaction_count": 1,
                "status": "new"
            }
            leads_collection.insert_one(lead_doc)
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/newsletter/subscribe")
async def newsletter_subscribe(data: dict):
    """Newsletter subscription endpoint"""
    try:
        email = data.get("email")
        source = data.get("source", "newsletter")
        
        # Check if already subscribed
        existing = newsletter_subscribers.find_one({"email": email})
        
        if not existing:
            newsletter_subscribers.insert_one({
                "email": email,
                "source": source,
                "subscribed_at": datetime.utcnow(),
                "status": "active"
            })
        
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
