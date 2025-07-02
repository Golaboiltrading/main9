"""
Advanced MongoDB Injection Prevention and Input Validation
Addresses OWASP A03: Injection Vulnerabilities
"""

from fastapi import HTTPException, Request
from typing import Any, Dict, List, Union
import re
import html
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# REMOVED MongoSanitizer class and sanitize_request_middleware function

class InputValidator:
    """
    Enhanced input validation for trading platform
    """
    
    # Valid commodity types for oil & gas trading
    VALID_COMMODITIES = {
        'crude_oil', 'brent_crude', 'wti_crude', 'natural_gas', 'lng', 
        'lpg', 'gasoline', 'diesel', 'jet_fuel', 'heating_oil', 
        'gas_condensate', 'ngl', 'ethane', 'propane', 'butane'
    }
    
    # Valid trading hubs
    VALID_TRADING_HUBS = {
        'houston', 'singapore', 'rotterdam', 'dubai', 'london',
        'new_york', 'chicago', 'los_angeles', 'mumbai', 'tokyo'
    }
    
    @classmethod
    def validate_trade_data(cls, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation for trading data
        
        Args:
            trade_data: Dictionary containing trade information
            
        Returns:
            Validated and sanitized trade data
            
        Raises:
            HTTPException: If validation fails
        """
        validated = {}
        
        # Validate commodity
        commodity = trade_data.get('commodity', '').lower().strip()
        if not commodity:
            raise HTTPException(status_code=400, detail="Commodity is required")
        
        # Sanitize commodity name
        commodity = re.sub(r'[^a-zA-Z0-9_\s-]', '', commodity)
        commodity = commodity.replace(' ', '_').replace('-', '_')
        
        if commodity not in cls.VALID_COMMODITIES:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid commodity. Allowed: {', '.join(cls.VALID_COMMODITIES)}"
            )
        validated['commodity'] = commodity
        
        # Validate quantity
        try:
            quantity = float(trade_data.get('quantity', 0))
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be positive")
            if quantity > 1000000:  # Reasonable upper limit
                raise HTTPException(status_code=400, detail="Quantity too large")
            validated['quantity'] = quantity
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid quantity format")
        
        # Validate price
        try:
            price = float(trade_data.get('price', 0))
            if price <= 0:
                raise HTTPException(status_code=400, detail="Price must be positive")
            if price > 1000000:  # Reasonable upper limit
                raise HTTPException(status_code=400, detail="Price too high")
            validated['price'] = price
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail="Invalid price format")
        
        # Validate trading hub
        trading_hub = trade_data.get('trading_hub', '').lower().strip()
        if trading_hub:
            trading_hub = re.sub(r'[^a-zA-Z0-9_\s-]', '', trading_hub)
            trading_hub = trading_hub.replace(' ', '_').replace('-', '_')
            
            if trading_hub not in cls.VALID_TRADING_HUBS:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid trading hub. Allowed: {', '.join(cls.VALID_TRADING_HUBS)}"
                )
            validated['trading_hub'] = trading_hub
        
        # Validate and sanitize description
        description = trade_data.get('description', '')
        if description:
            description = html.escape(description)  # Prevent XSS
            description = re.sub(r'[<>"\';\\]', '', description)  # Remove dangerous chars
            if len(description) > 1000:
                description = description[:1000]
            validated['description'] = description.strip()
        
        # Validate contact information
        contact_email = trade_data.get('contact_email', '')
        if contact_email:
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, contact_email):
                raise HTTPException(status_code=400, detail="Invalid email format")
            validated['contact_email'] = contact_email.lower().strip()
        
        # Validate contact person name
        contact_person = trade_data.get('contact_person', '')
        if contact_person:
            contact_person = re.sub(r'[^a-zA-Z\s\'-]', '', contact_person)
            if len(contact_person) > 100:
                contact_person = contact_person[:100]
            validated['contact_person'] = contact_person.strip()
        
        # Validate phone number
        contact_phone = trade_data.get('contact_phone', '')
        if contact_phone:
            # Remove all non-digit characters except + and spaces
            phone_cleaned = re.sub(r'[^\d\+\s\-\(\)]', '', contact_phone)
            if len(phone_cleaned) < 7 or len(phone_cleaned) > 20:
                raise HTTPException(status_code=400, detail="Invalid phone number")
            validated['contact_phone'] = phone_cleaned
        
        return validated
    
    @classmethod
    def validate_search_filters(cls, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate search and filter parameters
        """
        validated = {}
        
        # Validate commodity filter
        if 'commodity' in filters:
            commodity = filters['commodity'].lower().strip()
            commodity = re.sub(r'[^a-zA-Z0-9_\s-]', '', commodity)
            if commodity in cls.VALID_COMMODITIES:
                validated['commodity'] = commodity
        
        # Validate price range
        if 'min_price' in filters:
            try:
                min_price = float(filters['min_price'])
                if min_price >= 0:
                    validated['min_price'] = min_price
            except (ValueError, TypeError):
                pass
        
        if 'max_price' in filters:
            try:
                max_price = float(filters['max_price'])
                if max_price > 0:
                    validated['max_price'] = max_price
            except (ValueError, TypeError):
                pass
        
        # Validate quantity range
        if 'min_quantity' in filters:
            try:
                min_quantity = float(filters['min_quantity'])
                if min_quantity >= 0:
                    validated['min_quantity'] = min_quantity
            except (ValueError, TypeError):
                pass
        
        # Validate location
        if 'location' in filters:
            location = filters['location'].lower().strip()
            location = re.sub(r'[^a-zA-Z0-9_\s-]', '', location)
            if len(location) <= 100:
                validated['location'] = location
        
        return validated

class FileUploadValidator:
    """
    Enhanced file upload security for document analysis
    """
    
    ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # File signature validation
    FILE_SIGNATURES = {
        '.pdf': [b'%PDF'],
        '.jpg': [b'\xff\xd8\xff'],
        '.jpeg': [b'\xff\xd8\xff'],
        '.png': [b'\x89PNG\r\n\x1a\n'],
        '.doc': [b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'],
        '.docx': [b'PK\x03\x04']
    }
    
    @classmethod
    def validate_upload(cls, file_content: bytes, filename: str, content_type: str) -> bool:
        """
        Comprehensive file upload validation
        
        Args:
            file_content: The file content as bytes
            filename: Original filename
            content_type: MIME content type
            
        Returns:
            True if file is valid
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate file size
        if len(file_content) > cls.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {cls.MAX_FILE_SIZE // (1024*1024)}MB"
            )
        
        if len(file_content) < 100:  # Minimum viable file size
            raise HTTPException(status_code=400, detail="File appears to be empty or corrupted")
        
        # Sanitize and validate filename
        filename = cls._sanitize_filename(filename)
        file_ext = filename.split('.')[-1].lower() if '.' in filename else ''
        file_ext = f'.{file_ext}'
        
        if file_ext not in cls.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"File type not allowed. Allowed types: {', '.join(cls.ALLOWED_EXTENSIONS)}"
            )
        
        # Validate content type
        expected_content_types = {
            '.pdf': ['application/pdf'],
            '.jpg': ['image/jpeg'],
            '.jpeg': ['image/jpeg'], 
            '.png': ['image/png'],
            '.doc': ['application/msword'],
            '.docx': ['application/vnd.openxmlformats-officedocument.wordprocessingml.document']
        }
        
        if file_ext in expected_content_types:
            if content_type not in expected_content_types[file_ext]:
                raise HTTPException(
                    status_code=400,
                    detail="File content type doesn't match extension"
                )
        
        # Validate file signature (magic bytes)
        if file_ext in cls.FILE_SIGNATURES:
            valid_signature = False
            for signature in cls.FILE_SIGNATURES[file_ext]:
                if file_content.startswith(signature):
                    valid_signature = True
                    break
            
            if not valid_signature:
                raise HTTPException(
                    status_code=400,
                    detail="File appears to be corrupted or malicious"
                )
        
        # Additional security checks
        cls._scan_for_malicious_content(file_content, file_ext)
        
        return True
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent directory traversal"""
        import os
        
        # Remove path components
        filename = os.path.basename(filename)
        
        # Remove dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    @staticmethod
    def _scan_for_malicious_content(file_content: bytes, file_ext: str):
        """Basic malicious content detection"""
        
        # Check for embedded scripts or executables
        malicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onerror=',
            b'\x4d\x5a',  # PE executable header
            b'\x50\x4b\x05\x06',  # ZIP end signature (could be malicious archive)
        ]
        
        content_lower = file_content.lower()
        for pattern in malicious_patterns:
            if pattern in content_lower:
                logger.warning(f"Malicious pattern detected in file: {pattern}")
                raise HTTPException(
                    status_code=400,
                    detail="File contains potentially malicious content"
                )

# Middleware for automatic request sanitization
async def sanitize_request_middleware(request: Request, call_next):
    """
    Middleware to automatically sanitize incoming requests
    """
    # This middleware is being removed. Pydantic validation at the endpoint level is preferred.
    # try:
    #     # Only process JSON requests
    #     if request.headers.get('content-type') == 'application/json':
    #         body = await request.body()
    #         if body:
    #             try:
    #                 data = json.loads(body)
    #                 # Sanitize the request data
    #                 # if isinstance(data, dict):
    #                 #     sanitized_data = MongoSanitizer.sanitize_query(data) # MongoSanitizer is removed
    #                     # Note: In a real implementation, you'd need to modify the request body
    #                     # This is a simplified example
    #             except json.JSONDecodeError:
    #                 pass

    response = await call_next(request)
    return response
    
    # except Exception as e:
    #     logger.error(f"Error in sanitization middleware: {e}")
    #     raise HTTPException(status_code=500, detail="Request processing error")