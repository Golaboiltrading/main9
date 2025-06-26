
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
        print("\n" + "="*50)
        print(f"🔍 OIL & GAS FINDER PLATFORM TESTING SUMMARY")
        print("="*50)
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Print details of failed tests
        if self.tests_passed < self.tests_run:
            print("\n❌ Failed tests:")
            for name, result in self.test_results.items():
                if not result.get('success'):
                    if 'expected_status' in result:
                        print(f"  - {name}: Expected status {result['expected_status']}, got {result['actual_status']}")
                        if result.get('content_check'):
                            print(f"    Content check: {result['content_check']}")
                    else:
                        print(f"  - {name}: {result.get('error', 'Unknown error')}")
        
        print("="*50)
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL from environment variable or use the default
    backend_url = "https://97cdbb83-8ee9-4f68-b3c2-729c6dd484c8.preview.emergentagent.com"
    
    print(f"Testing Oil & Gas Finder Platform API at: {backend_url}")
    
    # Initialize tester
    tester = OilGasFinderTester(backend_url)
    
    # Test SEO Infrastructure
    tester.test_sitemap_xml()
    tester.test_robots_txt()
    
    # Test Analytics & Lead Generation
    tester.test_newsletter_subscribe()
    tester.test_lead_capture()
    tester.test_analytics_pageview()
    tester.test_analytics_event()
    
    # Test Content APIs
    tester.test_blog_posts()
    tester.test_blog_post_by_slug()
    tester.test_blog_categories()
    tester.test_location_data()
    tester.test_product_data()
    
    # Test Platform Status
    tester.test_api_status()
    tester.test_platform_stats()
    tester.test_market_data()
    tester.test_market_intelligence()
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
