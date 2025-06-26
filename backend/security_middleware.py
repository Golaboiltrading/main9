from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
import bcrypt
from typing import List, Optional
import re

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

# Password security
def hash_password(password: str) -> str:
    """Hash password with bcrypt and salt rounds >= 12"""
    salt_rounds = 12
    salt = bcrypt.gensalt(rounds=salt_rounds)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# JWT token functions
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Role-based access control
class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        payload = verify_token(token)
        
        user_role = payload.get("role")
        user_id = payload.get("sub")
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied. Insufficient permissions."
            )
        
        return {"user_id": user_id, "role": user_role, "payload": payload}

# Specific role checkers
require_admin = RoleChecker(["admin"])
require_premium = RoleChecker(["admin", "premium", "enterprise"])
require_authenticated = RoleChecker(["admin", "premium", "enterprise", "basic"])

# Ownership verification
def verify_resource_ownership(resource_user_id: str, current_user: dict):
    """Verify user owns the resource or is admin"""
    if current_user["role"] == "admin":
        return True
    
    if current_user["user_id"] != resource_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. You can only access your own resources."
        )
    return True

# Input validation and sanitization
class InputValidator:
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        return email.lower().strip()
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength"""
        if len(password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            raise HTTPException(status_code=400, detail="Password must contain uppercase letter")
        
        if not re.search(r'[a-z]', password):
            raise HTTPException(status_code=400, detail="Password must contain lowercase letter")
        
        if not re.search(r'\d', password):
            raise HTTPException(status_code=400, detail="Password must contain number")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise HTTPException(status_code=400, detail="Password must contain special character")
        
        return password
    
    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 255) -> str:
        """Sanitize and validate string input"""
        if not input_str or not isinstance(input_str, str):
            raise HTTPException(status_code=400, detail="Invalid string input")
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\';\\]', '', input_str.strip())
        
        if len(sanitized) > max_length:
            raise HTTPException(status_code=400, detail=f"Input too long. Maximum {max_length} characters.")
        
        return sanitized
    
    @staticmethod
    def validate_commodity_type(commodity: str) -> str:
        """Validate commodity type against allowed values"""
        allowed_commodities = [
            'crude_oil', 'natural_gas', 'lng', 'gasoline', 
            'diesel', 'jet_fuel', 'heating_oil', 'lpg'
        ]
        
        commodity = commodity.lower().strip()
        if commodity not in allowed_commodities:
            raise HTTPException(status_code=400, detail="Invalid commodity type")
        
        return commodity
    
    @staticmethod
    def validate_numeric_positive(value, field_name: str):
        """Validate positive numeric values"""
        try:
            num_value = float(value)
            if num_value <= 0:
                raise HTTPException(status_code=400, detail=f"{field_name} must be positive")
            return num_value
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail=f"Invalid {field_name} format")

# MongoDB injection prevention
def sanitize_mongo_query(query_dict: dict) -> dict:
    """Sanitize MongoDB query to prevent injection"""
    sanitized = {}
    
    for key, value in query_dict.items():
        # Remove keys starting with $ (MongoDB operators)
        if isinstance(key, str) and key.startswith('$'):
            continue
        
        # Sanitize string values
        if isinstance(value, str):
            sanitized[key] = re.sub(r'[{}$]', '', value)
        elif isinstance(value, dict):
            sanitized[key] = sanitize_mongo_query(value)
        else:
            sanitized[key] = value
    
    return sanitized

# File upload security
class FileValidator:
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file_upload(file_content: bytes, filename: str, content_type: str):
        """Validate uploaded file for security"""
        # Check file size
        if len(file_content) > FileValidator.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum 10MB allowed.")
        
        # Check file extension
        file_ext = os.path.splitext(filename)[1].lower()
        if file_ext not in FileValidator.ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        # Validate content type
        allowed_content_types = {
            'application/pdf': ['.pdf'],
            'image/jpeg': ['.jpg', '.jpeg'],
            'image/png': ['.png'],
            'application/msword': ['.doc'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
        }
        
        if content_type not in allowed_content_types:
            raise HTTPException(status_code=400, detail="Invalid file content type")
        
        expected_extensions = allowed_content_types[content_type]
        if file_ext not in expected_extensions:
            raise HTTPException(status_code=400, detail="File extension doesn't match content type")
        
        # Basic file header validation
        FileValidator._validate_file_header(file_content, file_ext)
        
        return True
    
    @staticmethod
    def _validate_file_header(file_content: bytes, file_ext: str):
        """Validate file headers to prevent malicious uploads"""
        if len(file_content) < 10:
            raise HTTPException(status_code=400, detail="File appears to be corrupted")
        
        # File signature validation
        signatures = {
            '.pdf': [b'%PDF'],
            '.jpg': [b'\xff\xd8\xff'],
            '.jpeg': [b'\xff\xd8\xff'],
            '.png': [b'\x89PNG\r\n\x1a\n'],
        }
        
        if file_ext in signatures:
            header = file_content[:10]
            valid_signature = any(header.startswith(sig) for sig in signatures[file_ext])
            
            if not valid_signature:
                raise HTTPException(status_code=400, detail="File appears to be corrupted or malicious")

# Rate limiting configuration
class RateLimitConfig:
    # Different limits for different user tiers
    RATE_LIMITS = {
        'free': {'requests': 20, 'window': 900},      # 20 requests per 15 minutes
        'basic': {'requests': 100, 'window': 900},    # 100 requests per 15 minutes
        'premium': {'requests': 500, 'window': 900},  # 500 requests per 15 minutes
        'enterprise': {'requests': 2000, 'window': 900}, # 2000 requests per 15 minutes
        'admin': {'requests': 5000, 'window': 900}    # 5000 requests per 15 minutes
    }
    
    @staticmethod
    def get_user_limit(user_role: str = 'free'):
        """Get rate limit for user role"""
        return RateLimitConfig.RATE_LIMITS.get(user_role, RateLimitConfig.RATE_LIMITS['free'])

# Security headers middleware
class SecurityHeaders:
    @staticmethod
    def get_security_headers():
        """Generate security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }

# Audit logging
class SecurityAuditLogger:
    @staticmethod
    def log_security_event(event_type: str, user_id: str, details: dict, ip_address: str = None):
        """Log security events for audit trail"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "ip_address": ip_address,
            "details": details,
            "severity": SecurityAuditLogger._get_severity(event_type)
        }
        
        # In production, send to proper logging service
        print(f"SECURITY_AUDIT: {log_entry}")
        
        # Store in database for analysis
        # await security_logs_collection.insert_one(log_entry)
    
    @staticmethod
    def _get_severity(event_type: str) -> str:
        """Determine severity level"""
        high_severity_events = ['failed_login_attempt', 'unauthorized_access', 'suspicious_file_upload']
        medium_severity_events = ['password_change', 'role_change', 'admin_action']
        
        if event_type in high_severity_events:
            return 'HIGH'
        elif event_type in medium_severity_events:
            return 'MEDIUM'
        else:
            return 'LOW'