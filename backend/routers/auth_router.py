from fastapi import APIRouter, HTTPException, Depends, status, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


import uuid
import re # For basic validation fallback
from datetime import datetime, timedelta


# Attempt to import shared resources from server.py or other locations
# This part is crucial and might need adjustment based on final shared module structure
try:
    from backend.server import (
        users_collection,
        hash_password,
        verify_password,
        create_access_token,
        ACCESS_TOKEN_EXPIRE_MINUTES, # Constant
        UserRole, # Enum
        email_service, # Service
        TradingRole # Enum
    )
    # Security related flags and utilities that might be in server.py or security_middleware.py
    from backend.server import ENHANCED_SECURITY_AVAILABLE, RATE_LIMITING_AVAILABLE
    # Assuming InputValidator and SecurityAuditLogger are made available/imported in server.py or directly from security_middleware
    from backend.security_middleware import InputValidator, SecurityAuditLogger
    from backend.slowapi.util import get_remote_address # if slowapi is structured this way
except ImportError:
    # Fallback for some utilities if direct server import fails or for cleaner separation later
    # This indicates a need for a proper shared 'core' module
    print("Warning: Could not import all dependencies directly from server.py for auth_router. Some functionalities might be limited or need refactoring of shared modules.")
    # Define minimal fallbacks or raise error if essential components are missing
    ENHANCED_SECURITY_AVAILABLE = False
    RATE_LIMITING_AVAILABLE = False
    # `users_collection` and other critical components would ideally cause a startup error if not available.
    # For now, we proceed assuming they will be available. If not, runtime errors will occur.
    # A more robust approach involves a shared 'db' module for collections and 'core.security' for auth utils.
    pass


logger = logging.getLogger(__name__)
router = APIRouter()

# --- Pydantic Models ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    company_name: str = Field(..., min_length=1, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., min_length=2, max_length=100)
    trading_role: TradingRole # Assuming TradingRole is available (imported from server or defined here)

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
                "trading_role": "buyer" # Make sure TradingRole enum is accessible
            }
        }

class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


# --- Route Handlers ---
@router.post("/register", status_code=status.HTTP_201_CREATED) # Added status_code
async def register_user_route(user_data: UserCreate, request: Request): # Renamed to avoid conflict if imported directly
    try:
        if ENHANCED_SECURITY_AVAILABLE and hasattr(InputValidator, 'validate_email'):
            user_data.email = InputValidator.validate_email(user_data.email)
            user_data.password = InputValidator.validate_password(user_data.password)
            user_data.first_name = InputValidator.sanitize_string(user_data.first_name, 100)
            user_data.last_name = InputValidator.sanitize_string(user_data.last_name, 100)
            user_data.company_name = InputValidator.sanitize_string(user_data.company_name, 200)
            user_data.country = InputValidator.sanitize_string(user_data.country, 100)
            if user_data.phone:
                user_data.phone = InputValidator.sanitize_string(user_data.phone, 20)
        else:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', user_data.email):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")
            if len(user_data.password) < 8:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must be at least 8 characters")

        existing_user = await users_collection.find_one({"email": user_data.email})
        if existing_user:
            if ENHANCED_SECURITY_AVAILABLE and RATE_LIMITING_AVAILABLE and hasattr(SecurityAuditLogger, 'log_security_event'):
                SecurityAuditLogger.log_security_event(
                    "registration_attempt_duplicate",
                    "unknown",
                    {"email": user_data.email},
                    get_remote_address(request) if callable(get_remote_address) else "unknown_ip"
                )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

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
            "trading_role": user_data.trading_role.value, # Ensure enum value is stored
            "role": UserRole.BASIC.value, # Ensure enum value is stored
            "is_verified": False,
            "created_at": datetime.utcnow(),
            "last_login": None,
            "login_attempts": 0,
            "account_locked": False
        }

        await users_collection.insert_one(user_doc)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_id, "role": UserRole.BASIC.value},
            expires_delta=access_token_expires
        )

        if ENHANCED_SECURITY_AVAILABLE and RATE_LIMITING_AVAILABLE and hasattr(SecurityAuditLogger, 'log_security_event'):
            SecurityAuditLogger.log_security_event(
                "user_registration",
                user_id,
                {"email": user_data.email, "role": UserRole.BASIC.value},
                get_remote_address(request) if callable(get_remote_address) else "unknown_ip"
            )

        if email_service and hasattr(email_service, 'send_welcome_email'):
            try:
                await email_service.send_welcome_email(user_data.email, user_data.first_name)
            except Exception as e:
                logger.error(f"Failed to send welcome email: {e}")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error during registration")

    return {
        "message": "User registered successfully",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user_id,
            "email": user_data.email,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "role": UserRole.BASIC.value
        }
    }


@router.post("/login")
async def login_user_route(user_data: UserLogin): # Renamed to avoid conflict
    user = await users_collection.find_one({"email": user_data.email})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        # TODO: Implement login attempt tracking and account locking here if ENHANCED_SECURITY_AVAILABLE
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    await users_collection.update_one(
        {"user_id": user["user_id"]},
        {"$set": {"last_login": datetime.utcnow(), "login_attempts": 0}} # Reset login attempts
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["user_id"], "role": user.get("role", UserRole.BASIC.value)}, # Include role in token
        expires_delta=access_token_expires
    )

    # Log successful login if security audit is available
    # if ENHANCED_SECURITY_AVAILABLE and hasattr(SecurityAuditLogger, 'log_security_event'):
    #     SecurityAuditLogger.log_security_event("user_login", user["user_id"], {"email": user["email"]}, get_remote_address(request))


    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "user_id": user["user_id"],
            "email": user["email"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "role": user.get("role", UserRole.BASIC.value),
            "company_name": user.get("company_name"),
            "trading_role": user.get("trading_role")
        }
    }

# Example of how TradingRole might be defined if not imported
# from enum import Enum
# class TradingRole(str, Enum):
#     BUYER = "buyer"
#     SELLER = "seller"
#     BOTH = "both"
# class UserRole(str, Enum): # If not imported
#    BASIC = "basic"
#    PREMIUM = "premium"
#    ENTERPRISE = "enterprise"

# Note: The actual availability of imported objects like `users_collection`, `hash_password`, etc.,
# depends on how `backend.server` is structured and if these are truly importable directly.
# If `server.py` defines them and also creates the FastAPI `app` instance, direct imports
# into a router file can work but often signal a need for better structuring of shared components
# (e.g., a db.py for database session/collections, core/security.py for auth utilities).
# The `try-except ImportError` block is a temporary measure.
# The `get_remote_address` import might also need to point to `slowapi.util` if that's where it lives.
# The logger was not initialized with `logging.getLogger(__name__)` in the provided snippet, added it.
# Added .value for enum values when storing/returning them as strings.
# Added status_code=status.HTTP_201_CREATED for successful registration.
# Changed HTTPException status codes to use `status.HTTP_...` for clarity.
# Added a placeholder for login attempt tracking in the login route.
# Included role in the JWT token during login.
# The `request: Request` parameter was missing in login_user_route, which is needed for get_remote_address.
# However, get_remote_address is not used in the login route in this version. If it were, request would be needed.
# Corrected the import for TradingRole if it's an enum.
# Corrected `get_remote_address` usage check (it's a function, not an object with methods).
# Made sure enum values are used when assigning to `user_doc` and in token.
# Placeholder for `logging` import.
import logging # Added this line
