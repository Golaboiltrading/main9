
import requests
import sys
import json
import uuid
from datetime import datetime

class OilGasFinderAPITester:
    def __init__(self, base_url):
        self.base_url = base_url
        self.token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.user_id = None
        self.listing_id = None
        self.payment_id = None
        self.subscription_id = None
        self.referral_code = None
        self.lead_magnet_id = None
        self.article_id = None
        self.test_results = {}

    def run_test(self, name, method, endpoint, expected_status, data=None, auth=False):
        """Run a single API test"""
        url = f"{self.base_url}/api/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'

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
            
            # Store test result
            self.test_results[name] = {
                'success': success,
                'expected_status': expected_status,
                'actual_status': response.status_code
            }
            
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return success, response.json()
                except:
                    return success, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"Error details: {error_data}")
                    return success, error_data
                except:
                    return success, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.test_results[name] = {
                'success': False,
                'error': str(e)
            }
            return False, {}

    def test_status(self):
        """Test API status endpoint"""
        return self.run_test("API Status", "GET", "status", 200)

    def test_register(self, email, password, first_name, last_name, company_name, country, trading_role):
        """Test user registration"""
        data = {
            "email": email,
            "password": password,
            "first_name": first_name,
            "last_name": last_name,
            "company_name": company_name,
            "country": country,
            "trading_role": trading_role
        }
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, data)
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['user_id']
        return success, response

    def test_login(self, email, password):
        """Test user login"""
        data = {
            "email": email,
            "password": password
        }
        success, response = self.run_test("User Login", "POST", "auth/login", 200, data)
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.user_id = response['user']['user_id']
        return success, response

    def test_get_profile(self):
        """Test getting user profile"""
        return self.run_test("Get User Profile", "GET", "user/profile", 200, auth=True)

    def test_get_stats(self):
        """Test getting platform statistics"""
        return self.run_test("Get Platform Stats", "GET", "stats", 200)

    def test_get_market_data(self):
        """Test getting market data"""
        return self.run_test("Get Market Data", "GET", "market-data", 200)

    def test_get_listings(self):
        """Test getting all listings"""
        return self.run_test("Get All Listings", "GET", "listings", 200)

    def test_create_listing(self):
        """Test creating a listing"""
        data = {
            "title": f"Test Listing {uuid.uuid4()}",
            "product_type": "crude_oil",
            "quantity": 100000,
            "unit": "barrels",
            "price_range": "$70-75 per barrel",
            "location": "Houston, TX",
            "trading_hub": "Houston, TX",
            "description": "Test listing for API testing",
            "contact_person": "Test Contact",
            "contact_email": "test@example.com",
            "contact_phone": "+1234567890",
            "is_featured": False
        }
        success, response = self.run_test("Create Listing", "POST", "listings", 200, data, auth=True)
        if success and 'listing_id' in response:
            self.listing_id = response['listing_id']
        return success, response

    def test_get_my_listings(self):
        """Test getting user's listings"""
        return self.run_test("Get My Listings", "GET", "listings/my", 200, auth=True)

    def test_update_listing(self):
        """Test updating a listing"""
        if not self.listing_id:
            print("❌ Cannot test update - no listing created")
            return False, {}
            
        data = {
            "title": f"Updated Test Listing {uuid.uuid4()}",
            "product_type": "crude_oil",
            "quantity": 150000,
            "unit": "barrels",
            "price_range": "$72-77 per barrel",
            "location": "Houston, TX",
            "trading_hub": "Houston, TX",
            "description": "Updated test listing for API testing",
            "contact_person": "Test Contact",
            "contact_email": "test@example.com",
            "contact_phone": "+1234567890",
            "is_featured": True
        }
        return self.run_test("Update Listing", "PUT", f"listings/{self.listing_id}", 200, data, auth=True)

    def test_delete_listing(self):
        """Test deleting a listing"""
        if not self.listing_id:
            print("❌ Cannot test delete - no listing created")
            return False, {}
            
        return self.run_test("Delete Listing", "DELETE", f"listings/{self.listing_id}", 200, auth=True)

    def test_search_companies(self):
        """Test searching companies"""
        return self.run_test("Search Companies", "GET", "search/companies", 200)

    def test_create_connection(self):
        """Test creating a connection to a listing"""
        # First, get a listing that's not owned by the current user
        success, response = self.run_test("Get Listings for Connection", "GET", "listings", 200)
        if not success or not response.get('listings'):
            print("❌ No listings available for connection test")
            return False, {}
            
        # Find a listing not owned by current user
        other_listing = None
        for listing in response.get('listings', []):
            if listing.get('user_id') != self.user_id:
                other_listing = listing
                break
                
        if not other_listing:
            print("❌ No listings from other users available for connection test")
            return False, {}
            
        return self.run_test("Create Connection", "POST", f"connections/{other_listing['listing_id']}", 200, auth=True)

    def test_get_connections(self):
        """Test getting user connections"""
        return self.run_test("Get Connections", "GET", "connections", 200, auth=True)

    # Payment API Tests
    def test_create_subscription_payment(self, tier="premium_basic"):
        """Test creating a subscription payment"""
        success, response = self.run_test("Create Subscription Payment", "POST", f"payments/create-subscription?tier={tier}", 200, auth=True)
        if success and 'subscription_id' in response:
            self.subscription_id = response['subscription_id']
            self.payment_id = response.get('payment_id')
        return success, response

    def test_create_featured_payment(self, listing_type="standard"):
        """Test creating a featured listing payment"""
        success, response = self.run_test("Create Featured Payment", "POST", f"payments/create-featured-payment?listing_type={listing_type}", 200, auth=True)
        if success and 'payment_id' in response:
            self.payment_id = response['payment_id']
        return success, response

    def test_execute_payment(self, payment_type="payment"):
        """Test executing a payment"""
        if not self.payment_id:
            print("❌ Cannot test payment execution - no payment created")
            return False, {}
            
        data = {
            "payment_id": self.payment_id,
            "payer_id": "TESTPAYERID12345",
            "payment_type": payment_type
        }
        return self.run_test("Execute Payment", "POST", "payments/execute", 200, data, auth=True)

    def test_get_payment_status(self):
        """Test getting payment status"""
        if not self.payment_id:
            print("❌ Cannot test payment status - no payment created")
            return False, {}
            
        return self.run_test("Get Payment Status", "GET", f"payments/status/{self.payment_id}", 200, auth=True)

    def test_cancel_subscription(self):
        """Test cancelling a subscription"""
        if not self.subscription_id:
            print("❌ Cannot test subscription cancellation - no subscription created")
            return False, {}
            
        return self.run_test("Cancel Subscription", "DELETE", f"payments/cancel-subscription/{self.subscription_id}", 200, auth=True)

    def test_get_payment_history(self):
        """Test getting payment history"""
        return self.run_test("Get Payment History", "GET", "payments/history", 200, auth=True)

    # Analytics API Tests
    def test_get_platform_analytics(self):
        """Test getting platform analytics"""
        return self.run_test("Get Platform Analytics", "GET", "analytics/platform", 200, auth=True)

    def test_get_user_analytics(self):
        """Test getting user analytics"""
        return self.run_test("Get User Analytics", "GET", "analytics/user", 200, auth=True)

    def test_get_market_analytics(self):
        """Test getting market analytics"""
        return self.run_test("Get Market Analytics", "GET", "analytics/market", 200)

    def test_get_revenue_analytics(self):
        """Test getting revenue analytics"""
        return self.run_test("Get Revenue Analytics", "GET", "analytics/revenue", 200, auth=True)

    def test_get_listing_analytics(self):
        """Test getting listing analytics"""
        if not self.listing_id:
            print("❌ Cannot test listing analytics - no listing created")
            return False, {}
            
        return self.run_test("Get Listing Analytics", "GET", f"analytics/listing/{self.listing_id}", 200, auth=True)

    # Email Notification Test
    def test_email_notification(self, email="test@example.com"):
        """Test email notification system"""
        return self.run_test("Test Email Notification", "POST", f"notifications/test-email?email={email}", 200, auth=True)

    # Business Growth API Tests
    def test_create_referral_program(self):
        """Test creating a referral program"""
        data = {
            "referral_type": "standard"
        }
        success, response = self.run_test("Create Referral Program", "POST", "referrals/create", 200, data, auth=True)
        if success and 'referral_code' in response:
            self.referral_code = response['referral_code']
        return success, response

    def test_process_referral_signup(self):
        """Test processing a referral signup"""
        if not self.referral_code:
            print("❌ Cannot test referral signup - no referral code created")
            return False, {}
            
        data = {
            "referral_code": self.referral_code
        }
        return self.run_test("Process Referral Signup", "POST", "referrals/signup", 200, data, auth=True)

    def test_process_referral_conversion(self):
        """Test processing a referral conversion"""
        if not self.user_id:
            print("❌ Cannot test referral conversion - no user ID available")
            return False, {}
            
        data = {
            "conversion_type": "subscription"
        }
        return self.run_test("Process Referral Conversion", "POST", f"referrals/convert/{self.user_id}", 200, data, auth=True)

    def test_get_conversion_metrics(self):
        """Test getting conversion metrics"""
        return self.run_test("Get Conversion Metrics", "GET", "referrals/metrics", 200, auth=True)

    def test_get_user_acquisition_dashboard(self):
        """Test getting user acquisition dashboard"""
        return self.run_test("Get User Acquisition Dashboard", "GET", "acquisition/dashboard", 200, auth=True)

    # Content Marketing API Tests
    def test_create_market_insight_article(self):
        """Test creating a market insight article"""
        data = {
            "title": f"Test Market Insight Article {uuid.uuid4().hex[:8]}",
            "content": "This is a test market insight article for API testing.",
            "category": "oil_market"
        }
        success, response = self.run_test("Create Market Insight Article", "POST", "content/article", 200, data, auth=True)
        if success and 'article_id' in response:
            self.article_id = response['article_id']
        return success, response

    def test_generate_weekly_market_report(self):
        """Test generating a weekly market report"""
        return self.run_test("Generate Weekly Market Report", "POST", "content/market-report", 200, auth=True)

    def test_create_seo_content(self):
        """Test creating SEO-optimized content"""
        data = {
            "topic": "Oil Price Trends 2025",
            "target_keywords": ["oil price forecast", "crude oil trends", "energy market outlook"],
            "content_type": "article"
        }
        return self.run_test("Create SEO Content", "POST", "content/seo-content", 200, data, auth=True)

    def test_generate_industry_whitepaper(self):
        """Test generating an industry whitepaper"""
        data = {
            "title": "Future of LNG Trading in Global Markets",
            "research_topic": "lng_market_trends"
        }
        return self.run_test("Generate Industry Whitepaper", "POST", "content/whitepaper", 200, data, auth=True)

    def test_get_content_performance(self):
        """Test getting content performance metrics"""
        return self.run_test("Get Content Performance", "GET", "content/performance", 200, auth=True)

    def test_get_content_marketing_dashboard(self):
        """Test getting content marketing dashboard"""
        return self.run_test("Get Content Marketing Dashboard", "GET", "content/dashboard", 200, auth=True)

    # Lead Generation API Tests
    def test_create_lead_magnet(self):
        """Test creating a lead magnet"""
        data = {
            "title": f"Test Lead Magnet {uuid.uuid4().hex[:8]}",
            "content_type": "whitepaper",
            "target_audience": "oil_traders"
        }
        success, response = self.run_test("Create Lead Magnet", "POST", "leads/magnet", 200, data, auth=True)
        if success and 'lead_magnet_id' in response:
            self.lead_magnet_id = response['lead_magnet_id']
        return success, response

    def test_track_lead_generation(self):
        """Test tracking lead generation"""
        if not self.lead_magnet_id:
            print("❌ Cannot test lead tracking - no lead magnet created")
            return False, {}
            
        data = {
            "lead_magnet_id": self.lead_magnet_id,
            "user_email": f"lead{uuid.uuid4().hex[:8]}@example.com",
            "source": "organic"
        }
        return self.run_test("Track Lead Generation", "POST", "leads/track", 200, data, auth=True)

    # Partnership API Tests
    def test_create_partnership_program(self):
        """Test creating a partnership program"""
        data = {
            "partner_type": "affiliate",
            "commission_rate": 20.0
        }
        return self.run_test("Create Partnership Program", "POST", "partnerships/create", 200, data, auth=True)

    # Enhanced Market Intelligence API Test
    def test_get_market_intelligence(self):
        """Test getting enhanced market intelligence"""
        return self.run_test("Get Market Intelligence", "GET", "market-intelligence", 200)

    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*50)
        print(f"🔍 API TESTING SUMMARY")
        print("="*50)
        print(f"✅ Tests passed: {self.tests_passed}/{self.tests_run} ({self.tests_passed/self.tests_run*100:.1f}%)")
        
        # Print details of failed tests
        if self.tests_passed < self.tests_run:
            print("\n❌ Failed tests:")
            for name, result in self.test_results.items():
                if not result.get('success'):
                    if 'expected_status' in result:
                        print(f"  - {name}: Expected status {result['expected_status']}, got {result['actual_status']}")
                    else:
                        print(f"  - {name}: {result.get('error', 'Unknown error')}")
        
        print("="*50)
        return self.tests_passed == self.tests_run

def main():
    # Get the backend URL
    backend_url = "https://2feb79c7-fd63-4021-b0db-9197e62ab3af.preview.emergentagent.com"
    
    print(f"Testing API at: {backend_url}")
    
    # Initialize tester
    tester = OilGasFinderAPITester(backend_url)
    
    # Test API status
    tester.test_status()
    
    # Test authentication - try with enterprise user first
    success, _ = tester.test_login("enterprise@oilfinder.com", "password123")
    
    if not success:
        # If enterprise login fails, try with regular user
        success, _ = tester.test_login("john.doe@petroltrade.com", "password123")
        
        if not success:
            # If all logins fail, register a new user
            test_email = f"test.user{uuid.uuid4().hex[:8]}@example.com"
            tester.test_register(
                email=test_email,
                password="TestPassword123!",
                first_name="Test",
                last_name="User",
                company_name="Test Oil Trading Co",
                country="United States",
                trading_role="both"
            )
    
    # Test user profile
    tester.test_get_profile()
    
    # Test platform data
    tester.test_get_stats()
    tester.test_get_market_data()
    tester.test_get_listings()
    
    # Test listing operations
    tester.test_create_listing()
    tester.test_get_my_listings()
    tester.test_update_listing()
    
    # Test search
    tester.test_search_companies()
    
    # Test connections
    tester.test_create_connection()
    tester.test_get_connections()
    
    # Test payment features
    tester.test_create_subscription_payment("premium_basic")
    tester.test_get_payment_status()
    tester.test_execute_payment("subscription")
    tester.test_create_featured_payment("standard")
    tester.test_execute_payment()
    tester.test_get_payment_history()
    
    # Test analytics features
    tester.test_get_user_analytics()
    tester.test_get_market_analytics()
    tester.test_get_platform_analytics()
    tester.test_get_revenue_analytics()
    tester.test_get_listing_analytics()
    
    # Test business growth features
    tester.test_create_referral_program()
    tester.test_process_referral_signup()
    tester.test_process_referral_conversion()
    tester.test_get_conversion_metrics()
    tester.test_get_user_acquisition_dashboard()
    
    # Test content marketing features
    tester.test_create_market_insight_article()
    tester.test_generate_weekly_market_report()
    tester.test_create_seo_content()
    tester.test_generate_industry_whitepaper()
    tester.test_get_content_performance()
    tester.test_get_content_marketing_dashboard()
    
    # Test lead generation features
    tester.test_create_lead_magnet()
    tester.test_track_lead_generation()
    
    # Test partnership features
    tester.test_create_partnership_program()
    
    # Test enhanced market intelligence
    tester.test_get_market_intelligence()
    
    # Test email notification
    tester.test_email_notification()
    
    # Test subscription cancellation
    tester.test_cancel_subscription()
    
    # Test listing deletion (do this last)
    tester.test_delete_listing()
    
    # Print summary
    success = tester.print_summary()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
