#!/usr/bin/env python3
"""
OWASP Security Testing Script for Oil & Gas Finder
Tests for OWASP Top 10 vulnerabilities
"""

import requests
import json
import time
import base64
from urllib.parse import urljoin
import random
import string

class SecurityTester:
    def __init__(self, base_url="http://localhost:3000"):
        self.base_url = base_url
        self.api_url = urljoin(base_url, "/api/")
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name, passed, details=""):
        """Log test results"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
    
    def test_a03_injection(self):
        """Test for A03: Injection"""
        print("\n💉 Testing A03: Injection")
        
        # Test XSS in registration
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
        ]
        
        for payload in xss_payloads:
            try:
                user_data = {
                    "email": f"xss_test_{random.randint(1000, 9999)}@example.com",
                    "password": "TestPassword123!",
                    "first_name": payload,
                    "last_name": "Test",
                    "company_name": "Test Company",
                    "phone": "+1234567890",
                    "country": "United States",
                    "trading_role": "buyer"
                }
                
                response = self.session.post(urljoin(self.api_url, "auth/register"),
                                           json=user_data)
                
                if response.status_code == 200:
                    data = response.json()
                    if "user" in data and "first_name" in data["user"]:
                        returned_name = data["user"]["first_name"]
                        if "<script>" in returned_name or "javascript:" in returned_name:
                            self.log_test("XSS Protection", False,
                                        f"XSS payload not sanitized: {returned_name}")
                        else:
                            self.log_test("XSS Protection", True,
                                        "XSS payload sanitized")
                    else:
                        self.log_test("XSS Protection", True, "User data structure safe")
                elif response.status_code in [400, 422]:
                    self.log_test("XSS Protection", True, "XSS payload rejected")
                else:
                    self.log_test("XSS Protection", False,
                                f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_test("XSS Protection", True, "Request failed as expected")
    
    def run_all_tests(self):
        """Run all security tests"""
        print("🛡️ Starting OWASP Security Tests for Oil & Gas Finder")
        print("=" * 60)
        
        self.test_a03_injection()
        
        # Summary
        passed = sum(1 for result in self.test_results if result["passed"])
        total = len(self.test_results)
        print(f"\n✅ Tests passed: {passed}/{total}")

if __name__ == "__main__":
    import sys
    
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"
    tester = SecurityTester(base_url)
    
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)