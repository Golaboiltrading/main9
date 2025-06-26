import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '1m', target: 50 },  // Ramp up to 50 users
    { duration: '3m', target: 100 }, // Ramp up to 100 users
    { duration: '2m', target: 200 }, // Ramp up to 200 users
    { duration: '5m', target: 200 }, // Stay at 200 users (stress)
    { duration: '2m', target: 0 },   // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<2000'], // 95% of requests should be below 2s under stress
    'http_req_failed': ['rate<0.2'],     // Error rate should be below 20% under stress
    'errors': ['rate<0.2'],              // Custom error rate should be below 20%
  },
};

const BASE_URL = 'http://localhost:3000';

export default function() {
  // Stress test with rapid API calls
  let responses = http.batch([
    ['GET', `${BASE_URL}/api/status`],
    ['GET', `${BASE_URL}/api/listings`],
    ['GET', `${BASE_URL}/api/market-data/crude_oil`],
    ['GET', `${BASE_URL}/`],
  ]);

  // Check all responses
  for (let i = 0; i < responses.length; i++) {
    check(responses[i], {
      'Status is not 5xx': (r) => r.status < 500,
      'Response time OK': (r) => r.timings.duration < 5000,
    }) || errorRate.add(1);
  }

  // Stress test user registration
  let registrationData = {
    email: `stress_test_${Math.random()}@example.com`,
    password: 'StressTest123!',
    first_name: 'Stress',
    last_name: 'Test',
    company_name: 'Stress Test Company',
    phone: '+1234567890',
    country: 'United States',
    trading_role: 'buyer'
  };

  let registerResponse = http.post(`${BASE_URL}/api/auth/register`, JSON.stringify(registrationData), {
    headers: { 'Content-Type': 'application/json' },
  });

  check(registerResponse, {
    'Registration handles stress': (r) => r.status === 200 || r.status === 400 || r.status === 429,
  }) || errorRate.add(1);

  sleep(0.1); // Minimal sleep for stress testing
}