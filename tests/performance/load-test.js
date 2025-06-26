import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
export let errorRate = new Rate('errors');

export let options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    'http_req_duration': ['p(95)<500'], // 95% of requests should be below 500ms
    'http_req_failed': ['rate<0.1'],    // Error rate should be below 10%
    'errors': ['rate<0.1'],             // Custom error rate should be below 10%
  },
};

const BASE_URL = 'http://localhost:3000';

export default function() {
  // Test homepage
  let homeResponse = http.get(`${BASE_URL}/`);
  check(homeResponse, {
    'Homepage status is 200': (r) => r.status === 200,
    'Homepage loads in <2s': (r) => r.timings.duration < 2000,
  }) || errorRate.add(1);

  sleep(1);

  // Test API status
  let apiResponse = http.get(`${BASE_URL}/api/status`);
  check(apiResponse, {
    'API status is 200': (r) => r.status === 200,
    'API responds in <500ms': (r) => r.timings.duration < 500,
    'API returns JSON': (r) => r.headers['Content-Type'] && r.headers['Content-Type'].includes('application/json'),
  }) || errorRate.add(1);

  sleep(1);

  // Test listings endpoint
  let listingsResponse = http.get(`${BASE_URL}/api/listings`);
  check(listingsResponse, {
    'Listings status is 200': (r) => r.status === 200,
    'Listings responds in <1s': (r) => r.timings.duration < 1000,
  }) || errorRate.add(1);

  sleep(1);

  // Test market data
  let marketResponse = http.get(`${BASE_URL}/api/market-data/crude_oil`);
  check(marketResponse, {
    'Market data loads': (r) => r.status === 200 || r.status === 404,
  });

  sleep(2);
}