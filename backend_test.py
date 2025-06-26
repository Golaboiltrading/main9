
import requests
import sys
import json
import uuid
import time
import base64
from datetime import datetime
import xml.etree.ElementTree as ET
import re

class OilGasFinderTester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = {}
        self.session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        self.session = requests.Session()
        self.auth_token = None
        
    def run_test(self, name, method, endpoint, expected_status, data=None, is_api=True, check_content=None):
        """Run a single API test"""
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
            if method == 'GET':
                response = self.session.get(url, headers=headers)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers)
            elif method == 'OPTIONS':
                response = self.session.options(url, headers=headers)

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

    # SEO Infrastructure Tests
    def test_sitemap_xml(self):
        """Test sitemap.xml generation"""
        def check_sitemap_content(response):
            try:
                # Check if it's valid XML
                root = ET.fromstring(response.text)
                
                # Check if it has the correct namespace
                if root.tag != '{http://www.sitemaps.org/schemas/sitemap/0.9}urlset':
                    return False, "Invalid sitemap root element"
                
                # Check if it contains URLs
                urls = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                if not urls:
                    return False, "No URLs found in sitemap"
                
                # Check if URLs contain oilgasfinder.com domain
                domain_check = True
                for url in urls:
                    loc = url.find('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                    if loc is not None and 'oilgasfinder.com' not in loc.text:
                        domain_check = False
                        break
                
                if not domain_check:
                    return False, "URLs don't contain oilgasfinder.com domain"
                
                return True, f"Valid sitemap with {len(urls)} URLs"
            except Exception as e:
                return False, f"XML parsing error: {str(e)}"
        
        return self.run_test("Sitemap XML", "GET", "sitemap.xml", 200, is_api=False, check_content=check_sitemap_content)

    def test_robots_txt(self):
        """Test robots.txt file"""
        def check_robots_content(response):
            content = response.text
            
            # Check if it contains basic directives
            if 'User-agent: *' not in content:
                return False, "Missing User-agent directive"
            
            # Check if it references the sitemap
            if 'Sitemap: https://oilgasfinder.com/sitemap.xml' not in content:
                return False, "Missing sitemap reference"
            
            # Check if it has allow/disallow directives
            if 'Allow:' not in content or 'Disallow:' not in content:
                return False, "Missing Allow or Disallow directives"
            
            return True, "Valid robots.txt with required directives"
        
        return self.run_test("Robots.txt", "GET", "robots.txt", 200, is_api=False, check_content=check_robots_content)

    # Analytics & Lead Generation Tests
    def test_newsletter_subscribe(self):
        """Test newsletter subscription"""
        data = {
            "email": f"test.user{uuid.uuid4().hex[:8]}@example.com",
            "source": "homepage"
        }
        return self.run_test("Newsletter Subscribe", "POST", "newsletter/subscribe", 200, data)

    def test_lead_capture(self):
        """Test lead capture"""
        data = {
            "email": f"lead.user{uuid.uuid4().hex[:8]}@example.com",
            "name": "Test Lead",
            "company": "Test Oil Company",
            "phone": "+1234567890",
            "formType": "demo_request",
            "source": "product_page",
            "timestamp": int(datetime.utcnow().timestamp())
        }
        return self.run_test("Lead Capture", "POST", "leads", 200, data)

    def test_analytics_pageview(self):
        """Test analytics pageview tracking"""
        data = {
            "path": "/products/crude-oil",
            "title": "Crude Oil Trading | Oil & Gas Finder",
            "timestamp": int(datetime.utcnow().timestamp()),
            "sessionId": self.session_id,
            "referrer": "https://www.google.com",
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        return self.run_test("Analytics Pageview", "POST", "analytics/pageview", 200, data)

    def test_analytics_event(self):
        """Test analytics event tracking"""
        data = {
            "event": "lead_generated",
            "parameters": {
                "category": "lead_generation",
                "label": "newsletter",
                "value": 5,
                "sessionId": self.session_id,
                "path": "/products/crude-oil"
            }
        }
        return self.run_test("Analytics Event", "POST", "analytics/event", 200, data)

    # Content API Tests
    def test_blog_posts(self):
        """Test blog posts API"""
        return self.run_test("Blog Posts", "GET", "blog/posts?limit=10&offset=0", 200)

    def test_blog_post_by_slug(self):
        """Test individual blog post by slug"""
        return self.run_test("Blog Post by Slug", "GET", "blog/posts/oil-market-analysis-global-trends-2024", 200)

    def test_blog_categories(self):
        """Test blog categories API"""
        return self.run_test("Blog Categories", "GET", "blog/categories", 200)

    def test_location_data(self):
        """Test location data API"""
        return self.run_test("Location Data", "GET", "locations/houston-tx", 200)

    def test_product_data(self):
        """Test product data API"""
        return self.run_test("Product Data", "GET", "products/crude-oil", 200)

    # Platform Status Tests
    def test_api_status(self):
        """Test API status endpoint"""
        return self.run_test("API Status", "GET", "status", 200)

    def test_platform_stats(self):
        """Test platform statistics"""
        return self.run_test("Platform Stats", "GET", "stats", 200)

    def test_market_data(self):
        """Test market data API"""
        return self.run_test("Market Data", "GET", "market-data", 200)

    def test_market_intelligence(self):
        """Test market intelligence API"""
        return self.run_test("Market Intelligence", "GET", "market-intelligence", 200)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print(f"🔍 OIL & GAS FINDER PLATFORM TESTING SUMMARY")
        print("="*80)
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Group test results by category
        categories = {
            "Functional": [],
            "Security": [],
            "Performance": []
        }
        
        for name, result in self.test_results.items():
            if any(security_term in name for security_term in ["JWT", "Password", "Injection", "Rate", "CORS", "Header"]):
                categories["Security"].append((name, result))
            elif any(perf_term in name for perf_term in ["Performance", "Response Time", "Cache"]):
                categories["Performance"].append((name, result))
            else:
                categories["Functional"].append((name, result))
        
        # Print results by category
        for category, tests in categories.items():
            if tests:
                passed = sum(1 for _, result in tests if result.get('success', False))
                total = len(tests)
                print(f"\n{category} Tests: {passed}/{total} passed ({passed/total*100:.1f}%)")
        
        # Print details of failed tests
        if self.tests_passed < self.tests_run:
            print("\n❌ Failed tests:")
            for category, tests in categories.items():
                failed_tests = [(name, result) for name, result in tests if not result.get('success', False)]
                if failed_tests:
                    print(f"\n  {category} Failures:")
                    for name, result in failed_tests:
                        if 'expected_status' in result:
                            print(f"    - {name}: Expected status {result['expected_status']}, got {result['actual_status']}")
                            if result.get('content_check'):
                                print(f"      Content check: {result['content_check']}")
                        else:
                            print(f"    - {name}: {result.get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        return self.tests_passed == self.tests_run
        
    # SECURITY TESTS
    
    def register_test_user(self):
        """Register a test user and get auth token"""
        test_email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"
        test_password = "SecurePass123!"
        test_user_data = {
            "email": test_email,
            "password": test_password,
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        print(f"Registering test user: {test_email}")
        success, data = self.run_test("User Registration", "POST", "auth/register", 200, test_user_data)
        
        if success and isinstance(data, dict) and 'access_token' in data:
            self.auth_token = data.get("access_token")
            self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
            print(f"✅ User registered successfully, token obtained")
            return True
        else:
            print(f"❌ Failed to register user")
            
            # Try logging in if registration fails (user might already exist)
            login_success, login_data = self.run_test("User Login", "POST", "auth/login", 200, {
                "email": test_email,
                "password": test_password
            })
            
            if login_success and isinstance(login_data, dict) and 'access_token' in login_data:
                self.auth_token = login_data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.auth_token}"})
                print(f"✅ User login successful, token obtained")
                return True
            
            return False

    def test_jwt_token_security(self):
        """Test JWT token security features"""
        if not self.auth_token:
            print("❌ No auth token available for JWT security testing")
            self.test_results["JWT Token Security"] = {
                'success': False,
                'error': "No auth token available"
            }
            self.tests_run += 1
            return False, {}
        
        # Check token format and structure
        token_parts = self.auth_token.split('.')
        if len(token_parts) != 3:
            self.test_results["JWT Token Format"] = {
                'success': False,
                'error': f"Token does not have three parts: {self.auth_token[:10]}..."
            }
            self.tests_run += 1
            print(f"❌ Failed - JWT Token Format: Token does not have three parts")
            return False, {}
        
        # Decode payload
        try:
            # Fix padding for base64 decoding
            payload = token_parts[1]
            payload += '=' * (4 - len(payload) % 4) if len(payload) % 4 != 0 else ''
            decoded_payload = base64.b64decode(payload)
            payload_data = json.loads(decoded_payload)
            
            # Check for required fields
            required_fields = ['exp', 'sub']
            missing_fields = [field for field in required_fields if field not in payload_data]
            
            if missing_fields:
                self.test_results["JWT Required Fields"] = {
                    'success': False,
                    'error': f"Missing required fields: {missing_fields}"
                }
                self.tests_run += 1
                print(f"❌ Failed - JWT Required Fields: Missing fields: {missing_fields}")
            else:
                self.test_results["JWT Required Fields"] = {
                    'success': True,
                    'details': f"Token contains required fields: {required_fields}"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - JWT Required Fields: Token contains required fields")
            
            # Check for session tracking
            if 'session_id' in payload_data:
                self.test_results["JWT Session Tracking"] = {
                    'success': True,
                    'details': "Token contains session_id for tracking"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - JWT Session Tracking: Token contains session_id")
            else:
                self.test_results["JWT Session Tracking"] = {
                    'success': False,
                    'error': "Token does not contain session_id"
                }
                self.tests_run += 1
                print(f"❌ Failed - JWT Session Tracking: Token does not contain session_id")
            
            # Check for role information
            if 'role' in payload_data:
                self.test_results["JWT Role Information"] = {
                    'success': True,
                    'details': f"Token contains role information: {payload_data['role']}"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - JWT Role Information: Token contains role: {payload_data['role']}")
            else:
                self.test_results["JWT Role Information"] = {
                    'success': False,
                    'error': "Token does not contain role information"
                }
                self.tests_run += 1
                print(f"❌ Failed - JWT Role Information: Token does not contain role")
            
            # Check for issued at timestamp
            if 'iat' in payload_data:
                self.test_results["JWT Issued At Timestamp"] = {
                    'success': True,
                    'details': "Token contains issued at timestamp"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - JWT Issued At Timestamp: Token contains iat")
            else:
                self.test_results["JWT Issued At Timestamp"] = {
                    'success': False,
                    'error': "Token does not contain issued at timestamp"
                }
                self.tests_run += 1
                print(f"❌ Failed - JWT Issued At Timestamp: Token does not contain iat")
                
            return True, payload_data
                
        except Exception as e:
            self.test_results["JWT Token Decoding"] = {
                'success': False,
                'error': f"Failed to decode token: {str(e)}"
            }
            self.tests_run += 1
            print(f"❌ Failed - JWT Token Decoding: {str(e)}")
            return False, {}

    def test_password_security(self):
        """Test password security implementation"""
        # Test with weak password
        weak_password_user = {
            "email": f"weak_pass_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        weak_pass_success, weak_pass_data = self.run_test("Weak Password Validation", "POST", "auth/register", 400, weak_password_user)
        
        # Test with missing uppercase
        missing_upper_user = {
            "email": f"missing_upper_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123!",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        missing_upper_success, missing_upper_data = self.run_test("Password Uppercase Requirement", "POST", "auth/register", 400, missing_upper_user)
        
        # Test with strong password
        strong_password_user = {
            "email": f"strong_pass_{uuid.uuid4().hex[:8]}@example.com",
            "password": "StrongP@ssw0rd123",
            "first_name": "Test",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        strong_pass_success, strong_pass_data = self.run_test("Strong Password Acceptance", "POST", "auth/register", 200, strong_password_user)
        
        return weak_pass_success and missing_upper_success and strong_pass_success

    def test_injection_vulnerabilities(self):
        """Test protection against injection vulnerabilities"""
        
        # Test MongoDB injection in search
        mongo_injection_success, mongo_injection_data = self.run_test(
            "MongoDB Injection Prevention", 
            "GET", 
            "listings?$where=function()%20%7B%20return%20true%3B%20%7D", 
            200
        )
        
        # Test XSS in user registration
        xss_user = {
            "email": f"xss_test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "SecurePass123!",
            "first_name": "<script>alert('xss')</script>",
            "last_name": "User",
            "company_name": "Test Company",
            "phone": "+1234567890",
            "country": "United States",
            "trading_role": "buyer"
        }
        
        xss_success, xss_data = self.run_test("XSS Prevention in Registration", "POST", "auth/register", 400, xss_user)
        
        # Test SQL-like injection in listing creation
        if self.auth_token:
            sql_injection_listing = {
                "title": "Test Listing'; DROP TABLE listings; --",
                "product_type": "crude_oil",
                "quantity": 1000,
                "unit": "barrels",
                "price_range": "70-80",
                "location": "Houston",
                "trading_hub": "houston",
                "description": "Test description with SQL injection attempt",
                "contact_person": "Test Person",
                "contact_email": "test@example.com",
                "contact_phone": "+1234567890",
                "is_featured": False
            }
            
            sql_injection_success, sql_injection_data = self.run_test(
                "SQL Injection Prevention in Listings", 
                "POST", 
                "listings", 
                200, 
                sql_injection_listing
            )
            
            return mongo_injection_success and xss_success and sql_injection_success
        else:
            return mongo_injection_success and xss_success

    def test_rate_limiting(self):
        """Test rate limiting implementation"""
        
        # Test authentication endpoint rate limiting (5 requests/minute)
        print("Testing authentication endpoint rate limiting...")
        auth_start_time = time.time()
        auth_success_count = 0
        auth_limited_count = 0
        
        for i in range(7):  # Try 7 requests (should be limited after 5)
            login_data = {
                "email": f"nonexistent_{i}@example.com",
                "password": "WrongPassword123!"
            }
            
            response = self.session.post(f"{self.base_url}/api/auth/login", json=login_data)
            
            if response.status_code == 429:
                auth_limited_count += 1
                print(f"  Request {i+1}: Rate limited (429)")
            else:
                auth_success_count += 1
                print(f"  Request {i+1}: Status {response.status_code}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.5)
        
        auth_elapsed_time = time.time() - auth_start_time
        
        if auth_limited_count > 0:
            self.test_results["Authentication Rate Limiting"] = {
                'success': True,
                'details': f"Rate limiting activated after {auth_success_count} requests in {auth_elapsed_time:.2f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Authentication Rate Limiting: Activated after {auth_success_count} requests")
        else:
            self.test_results["Authentication Rate Limiting"] = {
                'success': False,
                'error': f"No rate limiting observed after {auth_success_count} requests"
            }
            self.tests_run += 1
            print(f"❌ Failed - Authentication Rate Limiting: No rate limiting observed")
        
        # Test general API rate limiting
        print("Testing general API rate limiting...")
        api_start_time = time.time()
        api_success_count = 0
        api_limited_count = 0
        
        for i in range(60):  # Try a large number of requests to trigger rate limiting
            response = self.session.get(f"{self.base_url}/api/status")
            
            if response.status_code == 429:
                api_limited_count += 1
                print(f"  Request {i+1}: Rate limited (429)")
                # Once we hit the rate limit, we can stop
                if api_limited_count >= 3:
                    break
            else:
                api_success_count += 1
                if i % 10 == 0:
                    print(f"  Request {i+1}: Status {response.status_code}")
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1)
        
        api_elapsed_time = time.time() - api_start_time
        
        if api_limited_count > 0:
            self.test_results["General API Rate Limiting"] = {
                'success': True,
                'details': f"Rate limiting activated after {api_success_count} requests in {api_elapsed_time:.2f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - General API Rate Limiting: Activated after {api_success_count} requests")
            return True
        else:
            self.test_results["General API Rate Limiting"] = {
                'success': False,
                'error': f"No rate limiting observed after {api_success_count} requests"
            }
            self.tests_run += 1
            print(f"❌ Failed - General API Rate Limiting: No rate limiting observed")
            return False

    def test_security_headers(self):
        """Test security headers implementation"""
        
        response = self.session.get(f"{self.base_url}/api/status")
        
        # Check for required security headers
        headers = response.headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": None,  # Just check existence
            "Content-Security-Policy": None,    # Just check existence
            "Referrer-Policy": None             # Just check existence
        }
        
        all_headers_present = True
        
        for header, expected_value in security_headers.items():
            if header in headers:
                if expected_value is None or headers[header] == expected_value:
                    self.test_results[f"{header} Header"] = {
                        'success': True,
                        'details': f"Header present with value: {headers[header]}"
                    }
                    self.tests_run += 1
                    self.tests_passed += 1
                    print(f"✅ Passed - {header} Header: Present with value: {headers[header]}")
                else:
                    self.test_results[f"{header} Header"] = {
                        'success': False,
                        'error': f"Header present but with unexpected value: {headers[header]}"
                    }
                    self.tests_run += 1
                    print(f"❌ Failed - {header} Header: Unexpected value: {headers[header]}")
                    all_headers_present = False
            else:
                self.test_results[f"{header} Header"] = {
                    'success': False,
                    'error': "Header not present"
                }
                self.tests_run += 1
                print(f"❌ Failed - {header} Header: Not present")
                all_headers_present = False
        
        # Check CORS configuration
        options_response = self.session.options(f"{self.base_url}/api/status")
        
        if "Access-Control-Allow-Origin" in options_response.headers:
            allowed_origin = options_response.headers["Access-Control-Allow-Origin"]
            if allowed_origin != "*":
                self.test_results["CORS Configuration"] = {
                    'success': True,
                    'details': f"CORS configured with specific origin: {allowed_origin}"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - CORS Configuration: Specific origin: {allowed_origin}")
            else:
                self.test_results["CORS Configuration"] = {
                    'success': False,
                    'error': "CORS allows any origin (*)"
                }
                self.tests_run += 1
                print(f"❌ Failed - CORS Configuration: Allows any origin (*)")
                all_headers_present = False
        else:
            self.test_results["CORS Configuration"] = {
                'success': False,
                'error': "CORS headers not present"
            }
            self.tests_run += 1
            print(f"❌ Failed - CORS Configuration: Headers not present")
            all_headers_present = False
        
        return all_headers_present

    # PERFORMANCE TESTS
    
    def test_database_performance(self):
        """Test database performance with indexes"""
        
        # Test listings search performance
        print("Testing listings search performance...")
        
        # Warm up the endpoint
        self.session.get(f"{self.base_url}/api/listings")
        
        # Test with different filter combinations
        filter_combinations = [
            "listings",
            "listings?product_type=crude_oil",
            "listings?location=Houston",
            "listings?trading_hub=houston",
            "listings?product_type=natural_gas&location=Singapore"
        ]
        
        total_response_time = 0
        all_responses_fast = True
        
        for filter_url in filter_combinations:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/{filter_url}")
            elapsed_time = time.time() - start_time
            total_response_time += elapsed_time
            
            if response.status_code == 200:
                print(f"  Filter {filter_url}: {elapsed_time:.4f} seconds")
                if elapsed_time > 0.5:  # More than 500ms is slow
                    all_responses_fast = False
            else:
                print(f"  Filter {filter_url}: Failed with status {response.status_code}")
                all_responses_fast = False
        
        avg_response_time = total_response_time / len(filter_combinations)
        
        # For a well-indexed database, these queries should be fast
        if avg_response_time < 0.5:  # Less than 500ms average
            self.test_results["Listings Search Performance"] = {
                'success': True,
                'details': f"Average response time: {avg_response_time:.4f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Listings Search Performance: Avg time: {avg_response_time:.4f}s")
        else:
            self.test_results["Listings Search Performance"] = {
                'success': False,
                'error': f"Average response time too slow: {avg_response_time:.4f} seconds"
            }
            self.tests_run += 1
            print(f"❌ Failed - Listings Search Performance: Too slow: {avg_response_time:.4f}s")
        
        # Test company search performance
        print("Testing company search performance...")
        
        # Warm up the endpoint
        self.session.get(f"{self.base_url}/api/search/companies")
        
        search_queries = [
            "search/companies",
            "search/companies?q=oil",
            "search/companies?country=United%20States",
            "search/companies?trading_role=buyer"
        ]
        
        total_response_time = 0
        
        for query in search_queries:
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/{query}")
            elapsed_time = time.time() - start_time
            total_response_time += elapsed_time
            
            if response.status_code == 200:
                print(f"  Query {query}: {elapsed_time:.4f} seconds")
                if elapsed_time > 0.5:  # More than 500ms is slow
                    all_responses_fast = False
            else:
                print(f"  Query {query}: Failed with status {response.status_code}")
                all_responses_fast = False
        
        avg_response_time = total_response_time / len(search_queries)
        
        if avg_response_time < 0.5:  # Less than 500ms average
            self.test_results["Company Search Performance"] = {
                'success': True,
                'details': f"Average response time: {avg_response_time:.4f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Company Search Performance: Avg time: {avg_response_time:.4f}s")
        else:
            self.test_results["Company Search Performance"] = {
                'success': False,
                'error': f"Average response time too slow: {avg_response_time:.4f} seconds"
            }
            self.tests_run += 1
            print(f"❌ Failed - Company Search Performance: Too slow: {avg_response_time:.4f}s")
        
        return all_responses_fast

    def test_api_performance(self):
        """Test API performance and optimizations"""
        
        # Test market data endpoint performance
        print("Testing market data endpoint performance...")
        
        # Warm up the endpoint
        self.session.get(f"{self.base_url}/api/market-data")
        
        # Measure response time for multiple requests
        market_data_times = []
        
        for i in range(5):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/market-data")
            elapsed_time = time.time() - start_time
            market_data_times.append(elapsed_time)
            
            if response.status_code == 200:
                print(f"  Request {i+1}: {elapsed_time:.4f} seconds")
            else:
                print(f"  Request {i+1}: Failed with status {response.status_code}")
        
        avg_market_data_time = sum(market_data_times) / len(market_data_times)
        
        if avg_market_data_time < 0.3:  # Less than 300ms average
            self.test_results["Market Data Endpoint Performance"] = {
                'success': True,
                'details': f"Average response time: {avg_market_data_time:.4f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Market Data Performance: Avg time: {avg_market_data_time:.4f}s")
        else:
            self.test_results["Market Data Endpoint Performance"] = {
                'success': False,
                'error': f"Average response time too slow: {avg_market_data_time:.4f} seconds"
            }
            self.tests_run += 1
            print(f"❌ Failed - Market Data Performance: Too slow: {avg_market_data_time:.4f}s")
        
        # Test platform stats endpoint performance
        print("Testing platform stats endpoint performance...")
        
        # Warm up the endpoint
        self.session.get(f"{self.base_url}/api/stats")
        
        # Measure response time for multiple requests
        stats_times = []
        
        for i in range(5):
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/stats")
            elapsed_time = time.time() - start_time
            stats_times.append(elapsed_time)
            
            if response.status_code == 200:
                print(f"  Request {i+1}: {elapsed_time:.4f} seconds")
            else:
                print(f"  Request {i+1}: Failed with status {response.status_code}")
        
        avg_stats_time = sum(stats_times) / len(stats_times)
        
        if avg_stats_time < 0.3:  # Less than 300ms average
            self.test_results["Platform Stats Endpoint Performance"] = {
                'success': True,
                'details': f"Average response time: {avg_stats_time:.4f} seconds"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Platform Stats Performance: Avg time: {avg_stats_time:.4f}s")
            return True
        else:
            self.test_results["Platform Stats Endpoint Performance"] = {
                'success': False,
                'error': f"Average response time too slow: {avg_stats_time:.4f} seconds"
            }
            self.tests_run += 1
            print(f"❌ Failed - Platform Stats Performance: Too slow: {avg_stats_time:.4f}s")
            return False

    def test_caching(self):
        """Test caching implementation"""
        
        # Test if caching is working by checking response times
        print("Testing caching implementation...")
        
        # First request should be slower (cache miss)
        start_time = time.time()
        first_response = self.session.get(f"{self.base_url}/api/market-data")
        first_request_time = time.time() - start_time
        
        print(f"  First request (potential cache miss): {first_request_time:.4f} seconds")
        
        # Second request should be faster (cache hit)
        start_time = time.time()
        second_response = self.session.get(f"{self.base_url}/api/market-data")
        second_request_time = time.time() - start_time
        
        print(f"  Second request (potential cache hit): {second_request_time:.4f} seconds")
        
        # Check for cache headers
        cache_headers = ["Cache-Control", "ETag", "Last-Modified"]
        has_cache_headers = any(header in second_response.headers for header in cache_headers)
        
        # Determine if caching is working based on response time improvement
        if second_request_time < first_request_time * 0.8:  # At least 20% faster
            self.test_results["Response Time Improvement"] = {
                'success': True,
                'details': f"Second request was {(1 - second_request_time/first_request_time)*100:.1f}% faster"
            }
            self.tests_run += 1
            self.tests_passed += 1
            print(f"✅ Passed - Response Time Improvement: {(1 - second_request_time/first_request_time)*100:.1f}% faster")
            
            if has_cache_headers:
                self.test_results["Cache Headers"] = {
                    'success': True,
                    'details': f"Response includes cache headers: {[h for h in cache_headers if h in second_response.headers]}"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - Cache Headers: Present")
                return True
            else:
                self.test_results["Cache Headers"] = {
                    'success': False,
                    'error': "Response does not include standard cache headers"
                }
                self.tests_run += 1
                print(f"❌ Failed - Cache Headers: Not present")
                return False
        else:
            self.test_results["Response Time Improvement"] = {
                'success': False,
                'error': f"No significant improvement in response time: {first_request_time:.4f}s vs {second_request_time:.4f}s"
            }
            self.tests_run += 1
            print(f"❌ Failed - Response Time Improvement: No improvement")
            
            if has_cache_headers:
                self.test_results["Cache Headers"] = {
                    'success': True,
                    'details': f"Response includes cache headers despite no performance improvement"
                }
                self.tests_run += 1
                self.tests_passed += 1
                print(f"✅ Passed - Cache Headers: Present despite no performance improvement")
                return False
            else:
                self.test_results["Cache Headers"] = {
                    'success': False,
                    'error': "No evidence of caching implementation"
                }
                self.tests_run += 1
                print(f"❌ Failed - Cache Headers: Not present")
                return False

def main():
    # Get the backend URL from environment variable or use the default
    backend_url = "https://97cdbb83-8ee9-4f68-b3c2-729c6dd484c8.preview.emergentagent.com"
    
    print(f"Testing Oil & Gas Finder Platform API at: {backend_url}")
    
    # Initialize tester
    tester = OilGasFinderTester(backend_url)
    
    # Register test user for authenticated tests
    tester.register_test_user()
    
    print("\n" + "="*80)
    print("SECURITY TESTS - OWASP TOP 10")
    print("="*80)
    
    print("\n--- A02: Cryptographic Failures Testing ---")
    tester.test_jwt_token_security()
    tester.test_password_security()
    
    print("\n--- A03: Injection Vulnerabilities Testing ---")
    tester.test_injection_vulnerabilities()
    
    print("\n--- Rate Limiting Testing ---")
    tester.test_rate_limiting()
    
    print("\n--- Security Headers Testing ---")
    tester.test_security_headers()
    
    print("\n" + "="*80)
    print("PERFORMANCE TESTS")
    print("="*80)
    
    print("\n--- Database Performance ---")
    tester.test_database_performance()
    
    print("\n--- API Performance ---")
    tester.test_api_performance()
    
    print("\n--- Caching Performance ---")
    tester.test_caching()
    
    # Test SEO Infrastructure
    print("\n" + "="*80)
    print("FUNCTIONAL TESTS")
    print("="*80)
    
    print("\n--- SEO Infrastructure ---")
    tester.test_sitemap_xml()
    tester.test_robots_txt()
    
    # Test Analytics & Lead Generation
    print("\n--- Analytics & Lead Generation ---")
    tester.test_newsletter_subscribe()
    tester.test_lead_capture()
    tester.test_analytics_pageview()
    tester.test_analytics_event()
    
    # Test Content APIs
    print("\n--- Content APIs ---")
    tester.test_blog_posts()
    tester.test_blog_post_by_slug()
    tester.test_blog_categories()
    tester.test_location_data()
    tester.test_product_data()
    
    # Test Platform Status
    print("\n--- Platform Status ---")
    tester.test_api_status()
    tester.test_platform_stats()
    tester.test_market_data()
    tester.test_market_intelligence()
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
