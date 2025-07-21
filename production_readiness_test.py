#!/usr/bin/env python3

import requests
import sys
import json
import uuid
import time
import base64
from datetime import datetime
import xml.etree.ElementTree as ET
import re
import io
import os

class ProductionReadinessTest:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = {}
        self.session_id = f"prod_test_{uuid.uuid4().hex[:8]}"
        self.session = requests.Session()
        self.auth_token = None
        self.critical_failures = []
        
    def log_critical_failure(self, test_name, error):
        """Log critical failures that would block production deployment"""
        self.critical_failures.append({
            'test': test_name,
            'error': error,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    def run_test(self, name, method, endpoint, expected_status, data=None, is_api=True, check_content=None, critical=False):
        """Run a single API test with production readiness focus"""
        if is_api:
            url = f"{self.base_url}/api/{endpoint}"
        else:
            url = f"{self.base_url}/{endpoint}"
            
        headers = {'Content-Type': 'application/json'}
        if self.auth_token:
            headers['Authorization'] = f'Bearer {self.auth_token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = self.session.get(url, headers=headers, timeout=10)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, timeout=10)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers, timeout=10)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, timeout=10)
            elif method == 'OPTIONS':
                response = self.session.options(url, headers=headers, timeout=10)

            elapsed_time = time.time() - start_time
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
                'response_time': elapsed_time,
                'content_check': content_check_details if check_content else None,
                'critical': critical
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code} ({elapsed_time:.3f}s)")
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
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                if critical:
                    self.log_critical_failure(name, error_msg)
                print(f"❌ Failed - {error_msg} ({elapsed_time:.3f}s)")
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

        except requests.exceptions.Timeout:
            error_msg = "Request timeout (>10s)"
            if critical:
                self.log_critical_failure(name, error_msg)
            print(f"❌ Failed - {error_msg}")
            self.test_results[name] = {
                'success': False,
                'error': error_msg,
                'critical': critical
            }
            return False, {}
        except Exception as e:
            error_msg = str(e)
            if critical:
                self.log_critical_failure(name, error_msg)
            print(f"❌ Failed - Error: {error_msg}")
            self.test_results[name] = {
                'success': False,
                'error': error_msg,
                'critical': critical
            }
            return False, {}

    # CRITICAL AUTHENTICATION & SECURITY TESTS
    
    def test_user_registration_and_login(self):
        """Test user registration and login functionality - CRITICAL"""
        print("\n=== CRITICAL: Authentication System ===")
        
        # Test user registration
        test_email = f"prod_test_{uuid.uuid4().hex[:8]}@oilgascompany.com"
        test_password = "SecureOilGas2024!"
        
        registration_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Production",
            "last_name": "Tester",
            "company_name": "Oil & Gas Testing Corp",
            "phone": "+1-555-0123",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        reg_success, reg_data = self.run_test(
            "User Registration", 
            "POST", 
            "auth/register", 
            200, 
            registration_data,
            critical=True
        )
        
        if reg_success and isinstance(reg_data, dict) and 'access_token' in reg_data:
            self.auth_token = reg_data.get("access_token")
            print(f"✅ Registration successful, JWT token obtained")
            
            # Test login with same credentials
            login_data = {
                "email": test_email,
                "password": test_password
            }
            
            login_success, login_data = self.run_test(
                "User Login", 
                "POST", 
                "auth/login", 
                200, 
                login_data,
                critical=True
            )
            
            if login_success and isinstance(login_data, dict) and 'access_token' in login_data:
                print(f"✅ Login successful, JWT token obtained")
                return True
            else:
                self.log_critical_failure("User Login", "Failed to login with valid credentials")
                return False
        else:
            self.log_critical_failure("User Registration", "Failed to register new user")
            return False

    def test_jwt_token_security(self):
        """Test JWT token security and structure - CRITICAL"""
        if not self.auth_token:
            self.log_critical_failure("JWT Token Security", "No auth token available")
            return False
        
        print("\n=== CRITICAL: JWT Token Security ===")
        
        # Decode and validate JWT structure
        try:
            token_parts = self.auth_token.split('.')
            if len(token_parts) != 3:
                self.log_critical_failure("JWT Token Structure", "Token does not have three parts")
                return False
            
            # Decode payload
            payload = token_parts[1]
            payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
            decoded_payload = base64.b64decode(payload)
            payload_data = json.loads(decoded_payload)
            
            # Check required fields
            required_fields = ['exp', 'sub', 'iat']
            missing_fields = [field for field in required_fields if field not in payload_data]
            
            if missing_fields:
                self.log_critical_failure("JWT Required Fields", f"Missing fields: {missing_fields}")
                return False
            
            # Check expiration
            exp_timestamp = payload_data.get('exp')
            current_timestamp = time.time()
            
            if exp_timestamp <= current_timestamp:
                self.log_critical_failure("JWT Expiration", "Token is expired")
                return False
            
            print(f"✅ JWT token structure valid with expiration in {(exp_timestamp - current_timestamp)/60:.1f} minutes")
            return True
            
        except Exception as e:
            self.log_critical_failure("JWT Token Decoding", f"Failed to decode token: {str(e)}")
            return False

    def test_password_security(self):
        """Test password security requirements - CRITICAL"""
        print("\n=== CRITICAL: Password Security ===")
        
        # Test weak password rejection
        weak_passwords = [
            "password",
            "123456",
            "password123",
            "12345678"
        ]
        
        weak_password_rejected = True
        
        for weak_pass in weak_passwords:
            weak_user_data = {
                "email": f"weak_test_{uuid.uuid4().hex[:4]}@example.com",
                "password": weak_pass,
                "first_name": "Test",
                "last_name": "User",
                "company_name": "Test Company",
                "phone": "+1234567890",
                "country": "United States",
                "trading_role": "buyer"
            }
            
            success, data = self.run_test(
                f"Weak Password Rejection ({weak_pass})", 
                "POST", 
                "auth/register", 
                400, 
                weak_user_data
            )
            
            if not success:
                weak_password_rejected = False
                self.log_critical_failure("Password Security", f"Weak password '{weak_pass}' was accepted")
        
        if weak_password_rejected:
            print(f"✅ All weak passwords properly rejected")
            return True
        else:
            return False

    def test_rate_limiting(self):
        """Test rate limiting implementation - CRITICAL"""
        print("\n=== CRITICAL: Rate Limiting ===")
        
        # Test authentication endpoint rate limiting
        print("Testing authentication rate limiting...")
        
        rate_limited = False
        for i in range(8):  # Try 8 requests to trigger rate limiting
            login_data = {
                "email": f"nonexistent_{i}@example.com",
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 429:
                rate_limited = True
                print(f"✅ Rate limiting activated after {i+1} requests")
                break
            
            time.sleep(0.2)  # Small delay
        
        if not rate_limited:
            self.log_critical_failure("Rate Limiting", "No rate limiting observed on auth endpoints")
            return False
        
        return True

    def test_security_headers(self):
        """Test security headers implementation - CRITICAL"""
        print("\n=== CRITICAL: Security Headers ===")
        
        response = self.session.get(f"{self.base_url}/api/status")
        headers = response.headers
        
        required_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,
            "Content-Security-Policy": None,
            "Referrer-Policy": None
        }
        
        missing_headers = []
        
        for header, expected_value in required_headers.items():
            if header not in headers:
                missing_headers.append(header)
            elif expected_value and headers[header] != expected_value:
                missing_headers.append(f"{header} (incorrect value)")
        
        if missing_headers:
            self.log_critical_failure("Security Headers", f"Missing headers: {missing_headers}")
            return False
        
        print(f"✅ All required security headers present")
        return True

    def test_cors_configuration(self):
        """Test CORS configuration - CRITICAL"""
        print("\n=== CRITICAL: CORS Configuration ===")
        
        options_response = self.session.options(f"{self.base_url}/api/status")
        
        if "Access-Control-Allow-Origin" not in options_response.headers:
            self.log_critical_failure("CORS Configuration", "CORS headers not present")
            return False
        
        allowed_origin = options_response.headers["Access-Control-Allow-Origin"]
        
        # Check that CORS is not wildcard (security risk)
        if allowed_origin == "*":
            self.log_critical_failure("CORS Configuration", "CORS allows any origin (*) - security risk")
            return False
        
        print(f"✅ CORS properly configured with origin: {allowed_origin}")
        return True

    # CRITICAL BUSINESS LOGIC TESTS
    
    def test_listings_api_comprehensive(self):
        """Test listings API with all filter parameters - CRITICAL"""
        print("\n=== CRITICAL: Core Business Logic - Listings API ===")
        
        # Test basic listings endpoint
        success, data = self.run_test("Core Listings API", "GET", "listings", 200, critical=True)
        
        if not success or not isinstance(data, dict) or 'listings' not in data:
            self.log_critical_failure("Core Listings API", "Failed to retrieve listings")
            return False
        
        listings = data.get('listings', [])
        print(f"✅ Core listings API returned {len(listings)} listings")
        
        # Test product_type filtering
        product_types = ["crude_oil", "natural_gas", "gasoline", "diesel"]
        
        for product_type in product_types:
            success, filter_data = self.run_test(
                f"Product Filter ({product_type})", 
                "GET", 
                f"listings?product_type={product_type}", 
                200,
                critical=True
            )
            
            if success and isinstance(filter_data, dict) and 'listings' in filter_data:
                filtered_listings = filter_data['listings']
                # Verify all returned listings have correct product_type
                incorrect = [l for l in filtered_listings if l.get('product_type') != product_type]
                if incorrect:
                    self.log_critical_failure(f"Product Filter ({product_type})", 
                                            f"{len(incorrect)} listings have incorrect product_type")
                    return False
                print(f"✅ Product filter {product_type}: {len(filtered_listings)} listings")
        
        # Test listing_type filtering
        listing_types = ["buy", "sell"]
        
        for listing_type in listing_types:
            success, filter_data = self.run_test(
                f"Listing Type Filter ({listing_type})", 
                "GET", 
                f"listings?listing_type={listing_type}", 
                200,
                critical=True
            )
            
            if success and isinstance(filter_data, dict) and 'listings' in filter_data:
                filtered_listings = filter_data['listings']
                # Verify all returned listings have correct listing_type
                incorrect = [l for l in filtered_listings if l.get('listing_type') != listing_type]
                if incorrect:
                    self.log_critical_failure(f"Listing Type Filter ({listing_type})", 
                                            f"{len(incorrect)} listings have incorrect listing_type")
                    return False
                print(f"✅ Listing type filter {listing_type}: {len(filtered_listings)} listings")
        
        return True

    def test_listings_crud_operations(self):
        """Test listings CRUD operations - CRITICAL"""
        if not self.auth_token:
            self.log_critical_failure("Listings CRUD", "No auth token available")
            return False
        
        print("\n=== CRITICAL: Listings CRUD Operations ===")
        
        # Test listing creation
        listing_data = {
            "title": "Production Test Crude Oil Listing",
            "listing_type": "sell",
            "product_type": "crude_oil",
            "quantity": 50000,
            "unit": "barrels",
            "price_range": "75-80 USD/barrel",
            "location": "Houston, TX",
            "trading_hub": "Houston Ship Channel",
            "description": "High-quality West Texas Intermediate crude oil for immediate delivery",
            "contact_person": "Production Test Manager",
            "contact_email": "test@oilgascompany.com",
            "contact_phone": "+1-555-0123",
            "whatsapp_number": "+1-555-0123",
            "is_featured": False
        }
        
        create_success, create_data = self.run_test(
            "Create Listing", 
            "POST", 
            "listings", 
            200, 
            listing_data,
            critical=True
        )
        
        if not create_success or not isinstance(create_data, dict) or 'listing_id' not in create_data:
            self.log_critical_failure("Create Listing", "Failed to create listing")
            return False
        
        listing_id = create_data['listing_id']
        print(f"✅ Listing created with ID: {listing_id}")
        
        # Test listing update
        updated_data = listing_data.copy()
        updated_data['title'] = "Updated Production Test Listing"
        updated_data['price_range'] = "76-81 USD/barrel"
        
        update_success, update_data = self.run_test(
            "Update Listing", 
            "PUT", 
            f"listings/{listing_id}", 
            200, 
            updated_data,
            critical=True
        )
        
        if not update_success:
            self.log_critical_failure("Update Listing", "Failed to update listing")
            return False
        
        print(f"✅ Listing updated successfully")
        
        # Test listing deletion
        delete_success, delete_data = self.run_test(
            "Delete Listing", 
            "DELETE", 
            f"listings/{listing_id}", 
            200,
            critical=True
        )
        
        if not delete_success:
            self.log_critical_failure("Delete Listing", "Failed to delete listing")
            return False
        
        print(f"✅ Listing deleted successfully")
        return True

    def test_user_specific_listings(self):
        """Test user-specific listings endpoint - CRITICAL"""
        if not self.auth_token:
            self.log_critical_failure("User Listings", "No auth token available")
            return False
        
        print("\n=== CRITICAL: User-Specific Listings ===")
        
        success, data = self.run_test(
            "My Listings Endpoint", 
            "GET", 
            "listings/my", 
            200,
            critical=True
        )
        
        if not success or not isinstance(data, dict) or 'listings' not in data:
            self.log_critical_failure("My Listings Endpoint", "Failed to retrieve user listings")
            return False
        
        user_listings = data['listings']
        print(f"✅ User listings endpoint returned {len(user_listings)} listings")
        return True

    def test_file_upload_functionality(self):
        """Test file upload functionality for PDF documents - CRITICAL"""
        if not self.auth_token:
            self.log_critical_failure("File Upload", "No auth token available")
            return False
        
        print("\n=== CRITICAL: File Upload Functionality ===")
        
        # Create a test PDF file
        try:
            from reportlab.pdfgen import canvas
            
            buffer = io.BytesIO()
            c = canvas.Canvas(buffer)
            c.drawString(100, 100, "Production Test PDF Document")
            c.drawString(100, 120, "Oil & Gas Trading Procedure")
            c.drawString(100, 140, f"Generated: {datetime.utcnow().isoformat()}")
            c.save()
            buffer.seek(0)
            
            # Test file upload
            files = {'file': ('production_test.pdf', buffer, 'application/pdf')}
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            response = self.session.post(f"{self.base_url}/api/upload/procedure", files=files, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ PDF file upload successful")
                return True
            else:
                self.log_critical_failure("File Upload", f"Upload failed with status {response.status_code}")
                return False
                
        except ImportError:
            print("⚠️ Warning: reportlab not available, testing with dummy file")
            
            # Create dummy PDF content
            dummy_pdf = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000074 00000 n \n0000000120 00000 n \ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n179\n%%EOF"
            
            files = {'file': ('test.pdf', io.BytesIO(dummy_pdf), 'application/pdf')}
            headers = {'Authorization': f'Bearer {self.auth_token}'}
            
            response = self.session.post(f"{self.base_url}/api/upload/procedure", files=files, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ PDF file upload successful")
                return True
            else:
                self.log_critical_failure("File Upload", f"Upload failed with status {response.status_code}")
                return False
        
        except Exception as e:
            self.log_critical_failure("File Upload", f"Upload test failed: {str(e)}")
            return False

    # DATA INTEGRITY TESTS
    
    def test_database_connections(self):
        """Test database connections and operations - CRITICAL"""
        print("\n=== CRITICAL: Database Integrity ===")
        
        # Test platform stats (requires database queries)
        success, data = self.run_test(
            "Platform Statistics", 
            "GET", 
            "stats", 
            200,
            critical=True
        )
        
        if not success or not isinstance(data, dict):
            self.log_critical_failure("Database Connection", "Failed to retrieve platform statistics")
            return False
        
        # Verify expected fields in stats
        expected_fields = ['oil_gas_traders', 'active_oil_listings', 'successful_connections']
        missing_fields = [field for field in expected_fields if field not in data]
        
        if missing_fields:
            self.log_critical_failure("Database Integrity", f"Missing stats fields: {missing_fields}")
            return False
        
        print(f"✅ Database connection verified - {data.get('oil_gas_traders', 0)} traders, {data.get('active_oil_listings', 0)} listings")
        return True

    def test_data_validation(self):
        """Test data validation and sanitization - CRITICAL"""
        if not self.auth_token:
            self.log_critical_failure("Data Validation", "No auth token available")
            return False
        
        print("\n=== CRITICAL: Data Validation ===")
        
        # Test with invalid data
        invalid_listing = {
            "title": "",  # Empty title
            "listing_type": "invalid_type",  # Invalid enum
            "product_type": "crude_oil",
            "quantity": -1000,  # Negative quantity
            "unit": "barrels",
            "price_range": "invalid_price",
            "location": "",  # Empty location
            "trading_hub": "",
            "description": "",
            "contact_person": "",
            "contact_email": "invalid_email",  # Invalid email
            "contact_phone": "",
            "is_featured": False
        }
        
        success, data = self.run_test(
            "Data Validation", 
            "POST", 
            "listings", 
            400,  # Should return 400 for invalid data
            invalid_listing
        )
        
        if success:
            print(f"✅ Data validation working - invalid data properly rejected")
            return True
        else:
            self.log_critical_failure("Data Validation", "Invalid data was accepted")
            return False

    # API PERFORMANCE TESTS
    
    def test_api_response_times(self):
        """Test API response times for production readiness"""
        print("\n=== CRITICAL: API Performance ===")
        
        endpoints_to_test = [
            ("status", "GET", "status"),
            ("listings", "GET", "listings"),
            ("market-data", "GET", "market-data"),
            ("stats", "GET", "stats")
        ]
        
        all_fast = True
        
        for name, method, endpoint in endpoints_to_test:
            # Warm up
            self.session.get(f"{self.base_url}/api/{endpoint}")
            
            # Test multiple times
            times = []
            for _ in range(3):
                start_time = time.time()
                response = self.session.get(f"{self.base_url}/api/{endpoint}")
                elapsed = time.time() - start_time
                times.append(elapsed)
                
                if response.status_code != 200:
                    self.log_critical_failure(f"API Performance ({name})", f"Endpoint returned {response.status_code}")
                    all_fast = False
                    break
            
            avg_time = sum(times) / len(times)
            
            # Production threshold: 2 seconds max
            if avg_time > 2.0:
                self.log_critical_failure(f"API Performance ({name})", f"Average response time {avg_time:.3f}s exceeds 2s threshold")
                all_fast = False
            else:
                print(f"✅ {name} endpoint: {avg_time:.3f}s average response time")
        
        return all_fast

    def test_concurrent_requests(self):
        """Test concurrent request handling"""
        print("\n=== API Concurrency Test ===")
        
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_request():
            try:
                response = self.session.get(f"{self.base_url}/api/status")
                results.put(response.status_code == 200)
            except:
                results.put(False)
        
        # Create 10 concurrent requests
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = 0
        while not results.empty():
            if results.get():
                success_count += 1
        
        if success_count >= 8:  # Allow for some failures
            print(f"✅ Concurrent requests: {success_count}/10 successful")
            return True
        else:
            self.log_critical_failure("Concurrent Requests", f"Only {success_count}/10 requests successful")
            return False

    def test_error_handling(self):
        """Test error handling for edge cases"""
        print("\n=== Error Handling Test ===")
        
        # Test 404 handling
        success, data = self.run_test("404 Error Handling", "GET", "nonexistent-endpoint", 404)
        
        # Test invalid JSON
        try:
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                data="invalid json",
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code in [400, 422]:
                print(f"✅ Invalid JSON properly handled with status {response.status_code}")
                return True
            else:
                self.log_critical_failure("Error Handling", f"Invalid JSON returned status {response.status_code}")
                return False
        except Exception as e:
            self.log_critical_failure("Error Handling", f"Error handling test failed: {str(e)}")
            return False

    def print_production_readiness_summary(self):
        """Print comprehensive production readiness summary"""
        print("\n" + "="*100)
        print("🚀 PRODUCTION READINESS ASSESSMENT - OIL & GAS FINDER PLATFORM")
        print("="*100)
        
        # Calculate pass rates by category
        categories = {
            "Authentication & Security": [],
            "Core Business Logic": [],
            "Data Integrity": [],
            "API Performance": [],
            "Error Handling": []
        }
        
        # Categorize tests
        for name, result in self.test_results.items():
            if any(term in name for term in ["Authentication", "JWT", "Password", "Rate Limiting", "Security", "CORS"]):
                categories["Authentication & Security"].append((name, result))
            elif any(term in name for term in ["Listings", "CRUD", "Upload", "Filter"]):
                categories["Core Business Logic"].append((name, result))
            elif any(term in name for term in ["Database", "Validation", "Platform Statistics"]):
                categories["Data Integrity"].append((name, result))
            elif any(term in name for term in ["Performance", "Response Time", "Concurrent"]):
                categories["API Performance"].append((name, result))
            else:
                categories["Error Handling"].append((name, result))
        
        # Print category summaries
        overall_ready = True
        
        for category, tests in categories.items():
            if not tests:
                continue
                
            passed = sum(1 for _, result in tests if result.get('success', False))
            total = len(tests)
            critical_failed = sum(1 for _, result in tests if not result.get('success', False) and result.get('critical', False))
            
            status = "✅ READY" if passed == total else "❌ NOT READY" if critical_failed > 0 else "⚠️ WARNINGS"
            
            if critical_failed > 0:
                overall_ready = False
            
            print(f"\n{category}: {status}")
            print(f"  Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
            
            if critical_failed > 0:
                print(f"  🚨 CRITICAL FAILURES: {critical_failed}")
            
            # Show failed tests
            failed_tests = [(name, result) for name, result in tests if not result.get('success', False)]
            if failed_tests:
                print(f"  Failed tests:")
                for name, result in failed_tests[:3]:  # Show first 3
                    critical_marker = "🚨 " if result.get('critical', False) else "⚠️ "
                    error = result.get('error', f"Status {result.get('actual_status', 'unknown')}")
                    print(f"    {critical_marker}{name}: {error}")
        
        # Critical failures summary
        if self.critical_failures:
            print(f"\n🚨 CRITICAL FAILURES BLOCKING PRODUCTION DEPLOYMENT:")
            for failure in self.critical_failures:
                print(f"  - {failure['test']}: {failure['error']}")
        
        # Overall assessment
        print(f"\n{'='*100}")
        if overall_ready and not self.critical_failures:
            print("🎉 PRODUCTION DEPLOYMENT STATUS: ✅ READY")
            print("All critical systems are functioning correctly for production deployment.")
        else:
            print("🚨 PRODUCTION DEPLOYMENT STATUS: ❌ NOT READY")
            print("Critical issues must be resolved before production deployment.")
        
        print(f"\nOverall Test Results: {self.tests_passed}/{self.tests_run} passed ({self.tests_passed/self.tests_run*100:.1f}%)")
        print(f"Critical Failures: {len(self.critical_failures)}")
        print("="*100)
        
        return overall_ready and not self.critical_failures

def main():
    # Get backend URL from environment
    backend_url = None
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    backend_url = line.strip().split('=', 1)[1]
                    if backend_url.startswith('"') and backend_url.endswith('"'):
                        backend_url = backend_url[1:-1]
                    break
    except Exception as e:
        print(f"Error reading frontend/.env: {e}")
    
    if not backend_url:
        backend_url = "https://75613b56-3531-465e-8099-2cf9cff795d9.preview.emergentagent.com"
    
    print(f"🔍 PRODUCTION READINESS TESTING")
    print(f"Target: {backend_url}")
    print(f"Focus: Authentication, Security, Business Logic, Data Integrity, Performance")
    
    tester = ProductionReadinessTest(backend_url)
    
    # Run critical tests in order
    print("\n" + "="*80)
    print("EXECUTING PRODUCTION READINESS TEST SUITE")
    print("="*80)
    
    # 1. Authentication & Security Tests
    auth_success = tester.test_user_registration_and_login()
    if auth_success:
        tester.test_jwt_token_security()
    
    tester.test_password_security()
    tester.test_rate_limiting()
    tester.test_security_headers()
    tester.test_cors_configuration()
    
    # 2. Core Business Logic Tests
    tester.test_listings_api_comprehensive()
    if auth_success:
        tester.test_listings_crud_operations()
        tester.test_user_specific_listings()
        tester.test_file_upload_functionality()
    
    # 3. Data Integrity Tests
    tester.test_database_connections()
    if auth_success:
        tester.test_data_validation()
    
    # 4. API Performance Tests
    tester.test_api_response_times()
    tester.test_concurrent_requests()
    tester.test_error_handling()
    
    # Print final assessment
    production_ready = tester.print_production_readiness_summary()
    
    return 0 if production_ready else 1

if __name__ == "__main__":
    sys.exit(main())