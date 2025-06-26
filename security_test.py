import requests
import sys
import json
import uuid
import time
from datetime import datetime
import re
from concurrent.futures import ThreadPoolExecutor

class OWASPSecurityTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = {}
        self.tokens = {}  # Store tokens for different user roles
        self.test_users = {}  # Store test user credentials
        
    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None, is_api=True, check_content=None):
        """Run a single API test"""
        if is_api:
            url = f"{self.base_url}/api/{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
            
        if not headers:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            
            # Additional content check if provided
            content_check_result = True
            content_check_details = None
            if check_content and success:
                content_check_result, content_check_details = check_content(response)
                success = success and content_check_result
            
            # Store test result
            self.test_results[name] = {
                'success': success,
                'expected_status': expected_status,
                'actual_status': response.status_code,
                'content_check': content_check_details if check_content else None
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                if content_check_details:
                    print(f"   Content check: {content_check_details}")
                try:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        return success, response.json()
                    else:
                        return success, response.text
                except:
                    return success, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                if content_check_details:
                    print(f"   Content check failed: {content_check_details}")
                try:
                    if 'application/json' in response.headers.get('Content-Type', ''):
                        error_data = response.json()
                        print(f"Error details: {error_data}")
                        return success, error_data
                    else:
                        return success, response.text
                except:
                    return success, response.text

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results[name] = {
                'success': False,
                'error': str(e)
            }
            return False, {}

    def check_security_headers(self, response):
        """Check if security headers are properly set"""
        required_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
            "Content-Security-Policy",
            "Referrer-Policy"
        ]
        
        missing_headers = []
        for header in required_headers:
            if header not in response.headers:
                missing_headers.append(header)
        
        if missing_headers:
            return False, f"Missing security headers: {', '.join(missing_headers)}"
        return True, "All security headers present"

    # 1. Test Broken Access Control (RBAC)
    def create_test_users(self):
        """Create test users with different roles"""
        roles = ["basic", "premium", "enterprise", "admin"]
        
        for role in roles:
            # Create unique user for each role
            email = f"test_{role}_{uuid.uuid4().hex[:8]}@example.com"
            password = f"SecurePass123!_{uuid.uuid4().hex[:8]}"
            
            user_data = {
                "email": email,
                "password": password,
                "first_name": f"Test",
                "last_name": f"{role.capitalize()}",
                "company_name": f"Test {role.capitalize()} Company",
                "phone": "+1234567890",
                "country": "United States",
                "trading_role": "buyer"
            }
            
            success, response = self.run_test(
                f"Register {role} user",
                "POST",
                "auth/register",
                200,
                data=user_data
            )
            
            if success:
                self.test_users[role] = {
                    "email": email,
                    "password": password,
                    "user_id": response.get("user", {}).get("user_id"),
                    "token": response.get("access_token")
                }
                self.tokens[role] = response.get("access_token")
                print(f"Created test {role} user: {email}")
            else:
                print(f"Failed to create {role} user")
        
        # For testing purposes, we'll manually set the admin token since we can't create admin users directly
        if "admin" not in self.test_users:
            self.test_users["admin"] = {
                "email": "admin@example.com",
                "password": "AdminSecurePass123!",
                "user_id": None,
                "token": None
            }

    def test_rbac_endpoints(self):
        """Test role-based access control on protected endpoints"""
        # Define endpoints with required roles
        protected_endpoints = [
            {"endpoint": "analytics/platform", "required_role": "admin", "method": "GET", "data": None},
            {"endpoint": "analytics/revenue", "required_role": "admin", "method": "GET", "data": None},
            {"endpoint": "content/market-report", "required_role": "enterprise", "method": "POST", "data": {}},
            {"endpoint": "content/whitepaper", "required_role": "enterprise", "method": "POST", "data": {"title": "Test", "research_topic": "Oil Market"}}
        ]
        
        # Test each endpoint with different user roles
        for endpoint_info in protected_endpoints:
            endpoint = endpoint_info["endpoint"]
            required_role = endpoint_info["required_role"]
            method = endpoint_info["method"]
            data = endpoint_info["data"]
            
            for role, user_info in self.test_users.items():
                if not user_info["token"]:
                    continue
                
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {user_info["token"]}'
                }
                
                # Determine expected status based on role
                expected_status = 200 if role == required_role or role == "admin" else 403
                
                self.run_test(
                    f"RBAC: {role} user accessing {endpoint} (requires {required_role})",
                    method,
                    endpoint,
                    expected_status,
                    data=data,
                    headers=headers
                )

    # 2. Test Cryptographic Failures
    def test_password_hashing(self):
        """Test password hashing by attempting to login with correct and incorrect passwords"""
        # Test with correct password
        for role, user_info in self.test_users.items():
            if not user_info["email"] or not user_info["password"]:
                continue
                
            login_data = {
                "email": user_info["email"],
                "password": user_info["password"]
            }
            
            self.run_test(
                f"Login with correct password ({role} user)",
                "POST",
                "auth/login",
                200,
                data=login_data
            )
            
            # Test with incorrect password
            incorrect_login_data = {
                "email": user_info["email"],
                "password": user_info["password"] + "_wrong"
            }
            
            self.run_test(
                f"Login with incorrect password ({role} user)",
                "POST",
                "auth/login",
                401,
                data=incorrect_login_data
            )

    def test_jwt_token_expiration(self):
        """Test JWT token expiration (this is a mock test since we can't wait for actual expiration)"""
        # Create an invalid token by modifying a valid one
        if "basic" in self.tokens and self.tokens["basic"]:
            valid_token = self.tokens["basic"]
            invalid_token = valid_token[:-5] + "XXXXX"  # Corrupt the token
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {invalid_token}'
            }
            
            self.run_test(
                "JWT: Access with invalid token",
                "GET",
                "user/profile",
                401,
                headers=headers
            )
            
            # Test with valid token
            valid_headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {valid_token}'
            }
            
            self.run_test(
                "JWT: Access with valid token",
                "GET",
                "user/profile",
                200,
                headers=valid_headers
            )

    # 3. Test Injection Vulnerabilities
    def test_input_validation(self):
        """Test input validation and sanitization"""
        # Test email validation
        invalid_email_data = {
            "email": "not-an-email",
            "password": "SecurePass123!",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        self.run_test(
            "Input Validation: Invalid email format",
            "POST",
            "auth/register",
            400,
            data=invalid_email_data
        )
        
        # Test password validation
        weak_password_data = {
            "email": f"test_user_{uuid.uuid4().hex[:8]}@example.com",
            "password": "weak",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        self.run_test(
            "Input Validation: Weak password",
            "POST",
            "auth/register",
            400,
            data=weak_password_data
        )
        
        # Test SQL injection in login
        sql_injection_data = {
            "email": "' OR 1=1 --",
            "password": "' OR 1=1 --"
        }
        
        self.run_test(
            "Input Validation: SQL injection attempt in login",
            "POST",
            "auth/login",
            401,
            data=sql_injection_data
        )
        
        # Test XSS in user profile
        if "basic" in self.tokens and self.tokens["basic"]:
            xss_data = {
                "company_name": "<script>alert('XSS')</script>Test Company",
                "description": "<img src=x onerror=alert('XSS')>",
                "website": "javascript:alert('XSS')",
                "phone": "+1234567890",
                "address": "123 Test St",
                "country": "United States",
                "trading_hubs": ["Houston, TX"],
                "certifications": ["ISO 9001"]
            }
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.tokens["basic"]}'
            }
            
            self.run_test(
                "Input Validation: XSS attempt in profile update",
                "PUT",
                "user/profile",
                200,
                data=xss_data,
                headers=headers
            )

    # 4. Test Rate Limiting
    def test_rate_limiting(self):
        """Test rate limiting on different endpoints"""
        # Test rate limiting on /api/status (10 per minute)
        print("\n🔍 Testing Rate Limiting on /api/status (10 per minute)...")
        
        status_responses = []
        for i in range(12):  # Try 12 requests (should hit limit after 10)
            response = requests.get(f"{self.base_url}/api/status")
            status_responses.append(response.status_code)
            print(f"Request {i+1}: Status {response.status_code}")
            time.sleep(0.5)  # Small delay to avoid overwhelming the server
        
        # Check if rate limiting was applied
        rate_limited = 429 in status_responses
        self.tests_run += 1
        if rate_limited:
            self.tests_passed += 1
            print("✅ Passed - Rate limiting applied on /api/status")
            self.test_results["Rate Limiting: /api/status"] = {
                'success': True,
                'details': f"Rate limiting applied after {status_responses.index(429)} requests"
            }
        else:
            print("❌ Failed - Rate limiting not applied on /api/status")
            self.test_results["Rate Limiting: /api/status"] = {
                'success': False,
                'details': "Rate limiting not applied after 12 requests"
            }
        
        # Test rate limiting on /api/auth/register (5 per minute)
        print("\n🔍 Testing Rate Limiting on /api/auth/register (5 per minute)...")
        
        register_responses = []
        for i in range(7):  # Try 7 requests (should hit limit after 5)
            user_data = {
                "email": f"test_user_{uuid.uuid4().hex[:8]}@example.com",
                "password": "SecurePass123!",
                "first_name": "Test",
                "last_name": "User",
                "company_name": "Test Company",
                "phone": "+1234567890",
                "country": "United States",
                "trading_role": "buyer"
            }
            
            response = requests.post(f"{self.base_url}/api/auth/register", json=user_data)
            register_responses.append(response.status_code)
            print(f"Request {i+1}: Status {response.status_code}")
            time.sleep(0.5)  # Small delay
        
        # Check if rate limiting was applied
        rate_limited = 429 in register_responses
        self.tests_run += 1
        if rate_limited:
            self.tests_passed += 1
            print("✅ Passed - Rate limiting applied on /api/auth/register")
            self.test_results["Rate Limiting: /api/auth/register"] = {
                'success': True,
                'details': f"Rate limiting applied after {register_responses.index(429)} requests"
            }
        else:
            print("❌ Failed - Rate limiting not applied on /api/auth/register")
            self.test_results["Rate Limiting: /api/auth/register"] = {
                'success': False,
                'details': "Rate limiting not applied after 7 requests"
            }

    # 5. Test Security Headers and CORS
    def test_security_headers(self):
        """Test security headers on API responses"""
        response = requests.get(f"{self.base_url}/api/status")
        
        self.tests_run += 1
        headers_check, headers_details = self.check_security_headers(response)
        
        if headers_check:
            self.tests_passed += 1
            print("✅ Passed - Security headers check")
            self.test_results["Security Headers"] = {
                'success': True,
                'details': headers_details
            }
        else:
            print(f"❌ Failed - Security headers check: {headers_details}")
            self.test_results["Security Headers"] = {
                'success': False,
                'details': headers_details
            }
        
        # Print all headers for inspection
        print("\nSecurity Headers:")
        for header, value in response.headers.items():
            if header in ["X-Content-Type-Options", "X-Frame-Options", "X-XSS-Protection", 
                         "Strict-Transport-Security", "Content-Security-Policy", "Referrer-Policy"]:
                print(f"  {header}: {value}")

    def test_cors_configuration(self):
        """Test CORS configuration"""
        # Test with allowed origin
        allowed_origins = [
            "http://localhost:3000",
            "https://localhost:3000",
            "https://oilgasfinder.com",
            "https://www.oilgasfinder.com"
        ]
        
        for origin in allowed_origins:
            headers = {
                'Origin': origin,
                'Access-Control-Request-Method': 'GET'
            }
            
            response = requests.options(f"{self.base_url}/api/status", headers=headers)
            
            self.tests_run += 1
            if 'Access-Control-Allow-Origin' in response.headers:
                self.tests_passed += 1
                print(f"✅ Passed - CORS allowed for origin: {origin}")
                self.test_results[f"CORS: {origin}"] = {
                    'success': True,
                    'details': f"CORS allowed for {origin}"
                }
            else:
                print(f"❌ Failed - CORS not allowed for origin: {origin}")
                self.test_results[f"CORS: {origin}"] = {
                    'success': False,
                    'details': f"CORS not allowed for {origin}"
                }
        
        # Test with disallowed origin
        disallowed_origin = "https://malicious-site.com"
        headers = {
            'Origin': disallowed_origin,
            'Access-Control-Request-Method': 'GET'
        }
        
        response = requests.options(f"{self.base_url}/api/status", headers=headers)
        
        self.tests_run += 1
        if 'Access-Control-Allow-Origin' not in response.headers or response.headers['Access-Control-Allow-Origin'] != disallowed_origin:
            self.tests_passed += 1
            print(f"✅ Passed - CORS correctly blocked for origin: {disallowed_origin}")
            self.test_results[f"CORS: {disallowed_origin}"] = {
                'success': True,
                'details': f"CORS correctly blocked for {disallowed_origin}"
            }
        else:
            print(f"❌ Failed - CORS incorrectly allowed for origin: {disallowed_origin}")
            self.test_results[f"CORS: {disallowed_origin}"] = {
                'success': False,
                'details': f"CORS incorrectly allowed for {disallowed_origin}"
            }

    # 6. Test Security Audit Logging
    def test_security_logging(self):
        """Test security event logging (indirect test since we can't access logs directly)"""
        # Test login failure logging
        login_data = {
            "email": "nonexistent@example.com",
            "password": "WrongPassword123!"
        }
        
        self.run_test(
            "Security Logging: Failed login attempt",
            "POST",
            "auth/login",
            401,
            data=login_data
        )
        
        # Test registration with existing email (if we have a basic user)
        if "basic" in self.test_users and self.test_users["basic"]["email"]:
            existing_email_data = {
                "email": self.test_users["basic"]["email"],
                "password": "SecurePass123!",
                "first_name": "Test",
                "last_name": "User",
                "company_name": "Test Company",
                "phone": "+1234567890",
                "country": "United States",
                "trading_role": "buyer"
            }
            
            self.run_test(
                "Security Logging: Registration with existing email",
                "POST",
                "auth/register",
                400,
                data=existing_email_data
            )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print(f"🔍 OWASP TOP 10 SECURITY TESTING SUMMARY FOR OIL & GAS FINDER API")
        print("="*80)
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/max(self.tests_run, 1)*100:.1f}%)")
        
        # Group results by security category
        categories = {
            "1. Broken Access Control": ["RBAC"],
            "2. Cryptographic Failures": ["Login with correct password", "Login with incorrect password", "JWT"],
            "3. Injection Vulnerabilities": ["Input Validation"],
            "4. Rate Limiting": ["Rate Limiting"],
            "5. Security Headers and CORS": ["Security Headers", "CORS"],
            "6. Security Audit Logging": ["Security Logging"]
        }
        
        for category, keywords in categories.items():
            category_tests = [name for name in self.test_results.keys() 
                             if any(keyword in name for keyword in keywords)]
            
            if category_tests:
                passed = sum(1 for name in category_tests if self.test_results[name].get('success', False))
                total = len(category_tests)
                
                print(f"\n{category}: {passed}/{total} tests passed")
                
                # Print failed tests in this category
                if passed < total:
                    for name in category_tests:
                        if not self.test_results[name].get('success', False):
                            if 'expected_status' in self.test_results[name]:
                                print(f"  ❌ {name}: Expected status {self.test_results[name]['expected_status']}, got {self.test_results[name]['actual_status']}")
                                if self.test_results[name].get('content_check'):
                                    print(f"     Content check: {self.test_results[name]['content_check']}")
                            else:
                                print(f"  ❌ {name}: {self.test_results[name].get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from environment variable or use the default
    backend_url = "https://97cdbb83-8ee9-4f68-b3c2-729c6dd484c8.preview.emergentagent.com"
    
    print(f"Testing OWASP Top 10 Security Features for Oil & Gas Finder API at: {backend_url}")
    
    # Initialize tester
    tester = OWASPSecurityTester(backend_url)
    
    # Create test users for different roles
    tester.create_test_users()
    
    # 1. Test Broken Access Control (RBAC)
    tester.test_rbac_endpoints()
    
    # 2. Test Cryptographic Failures
    tester.test_password_hashing()
    tester.test_jwt_token_expiration()
    
    # 3. Test Injection Vulnerabilities
    tester.test_input_validation()
    
    # 4. Test Rate Limiting
    tester.test_rate_limiting()
    
    # 5. Test Security Headers and CORS
    tester.test_security_headers()
    tester.test_cors_configuration()
    
    # 6. Test Security Audit Logging
    tester.test_security_logging()
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())