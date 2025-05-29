# Oil & Gas Finder API Documentation

## Overview
The Oil & Gas Finder platform provides a comprehensive REST API for managing oil and gas trading operations, user authentication, premium subscriptions, analytics, and business intelligence.

**Base URL:** `https://oil-trade-hub.emergent.host/api`  
**Local Development:** `http://localhost:8001/api`

## Authentication
All authenticated endpoints require a Bearer token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Core API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /user/profile` - Get user profile (auth required)
- `PUT /user/profile` - Update user profile (auth required)

### Trading Listings
- `GET /listings` - Get all listings (with optional filters)
- `POST /listings` - Create new listing (auth required)
- `GET /listings/my` - Get user's listings (auth required)
- `PUT /listings/{listing_id}` - Update listing (auth required)
- `DELETE /listings/{listing_id}` - Delete listing (auth required)

### Connections & Networking
- `POST /connections/{listing_id}` - Create connection request (auth required)
- `GET /connections` - Get user connections (auth required)

### Platform Data
- `GET /status` - API status check
- `GET /stats` - Platform statistics
- `GET /market-data` - Oil & gas market data
- `GET /search/companies` - Search trading companies

## Premium Features

### Payment Processing
- `POST /payments/create-subscription` - Create premium subscription
- `POST /payments/create-featured-payment` - Payment for featured listings
- `POST /payments/execute` - Execute PayPal payment
- `GET /payments/status/{payment_id}` - Get payment status
- `GET /payments/history` - Get payment history (auth required)
- `DELETE /payments/cancel-subscription/{agreement_id}` - Cancel subscription

### Subscription Tiers
1. **Premium Basic** - $10/month
   - Enhanced listing visibility
   - Basic analytics dashboard
   - Priority customer support
   - Up to 20 listings per month

2. **Premium Advanced** - $25/month
   - Everything in Premium Basic
   - Advanced analytics & reporting
   - Unlimited featured listings
   - Market intelligence reports
   - Connection recommendations

3. **Enterprise** - $45/month
   - Everything in Premium Advanced
   - API access for integration
   - Custom branding options
   - Dedicated account manager
   - Advanced market insights

## Advanced Analytics

### User Analytics
- `GET /analytics/user` - Individual user performance metrics (auth required)

### Market Intelligence
- `GET /analytics/market` - Oil & gas market analytics and trends

### Business Intelligence
- `GET /analytics/platform` - Platform overview (enterprise users only)
- `GET /analytics/revenue` - Revenue analytics (enterprise users only)
- `GET /analytics/listing/{listing_id}` - Individual listing performance

## Email Notifications
- `POST /notifications/test-email` - Test email notification system

## Data Models

### User Registration
```json
{
  "email": "trader@company.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "Oil Trading Corp",
  "phone": "+1-555-123-4567",
  "country": "United States",
  "trading_role": "both" // "buyer", "seller", "both"
}
```

### Trading Listing
```json
{
  "title": "Premium WTI Crude Oil - 100,000 Barrels",
  "product_type": "crude_oil", // crude_oil, gasoline, diesel, jet_fuel, natural_gas, lng, lpg, gas_condensate
  "quantity": 100000,
  "unit": "barrels", // barrels, metric_tons, gallons, cubic_meters, mmbtu
  "price_range": "$75-78/barrel",
  "location": "Houston, Texas",
  "trading_hub": "Houston, TX", // Houston TX, Dubai UAE, Singapore, London UK, Rotterdam Netherlands, Cushing OK
  "description": "High-quality WTI crude oil available for immediate delivery...",
  "contact_person": "John Doe",
  "contact_email": "john.doe@company.com",
  "contact_phone": "+1-555-123-4567",
  "is_featured": false
}
```

### Market Data Response
```json
{
  "oil_prices": {
    "wti_crude": {"price": 78.45, "change": "+1.23", "updated": "2024-01-15T10:30:00Z"},
    "brent_crude": {"price": 82.15, "change": "+0.98", "updated": "2024-01-15T10:30:00Z"},
    "dubai_crude": {"price": 81.23, "change": "+1.05", "updated": "2024-01-15T10:30:00Z"}
  },
  "gas_prices": {
    "natural_gas": {"price": 2.85, "change": "-0.12", "updated": "2024-01-15T10:30:00Z"},
    "lng": {"price": 12.45, "change": "+0.23", "updated": "2024-01-15T10:30:00Z"}
  },
  "trading_hubs": ["Houston, TX", "Dubai, UAE", "Singapore", "London, UK", "Rotterdam, Netherlands", "Cushing, OK"]
}
```

### User Analytics Response
```json
{
  "user_info": {
    "user_id": "uuid",
    "company_name": "Oil Trading Corp",
    "country": "United States",
    "role": "premium",
    "trading_role": "both",
    "member_since": "2024-01-01T00:00:00Z"
  },
  "listings": {
    "total_listings": 15,
    "active_listings": 12,
    "featured_listings": 3,
    "product_breakdown": {
      "crude_oil": 8,
      "natural_gas": 4,
      "lng": 3
    }
  },
  "connections": {
    "connections_received": 45,
    "connections_made": 23,
    "successful_connections": 34,
    "connection_success_rate": 75.5
  },
  "financial": {
    "total_spent": 150.00,
    "subscription_status": "premium_advanced",
    "payment_history": [...]
  }
}
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error
- `503` - Service Unavailable

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting
- **Basic Users:** 100 requests per hour
- **Premium Users:** 500 requests per hour
- **Enterprise Users:** 2000 requests per hour

## Product Types Supported
- **Crude Oil:** WTI, Brent, Dubai, Regional grades
- **Refined Products:** Gasoline, Diesel, Jet fuel, Heating oil
- **Natural Gas:** Pipeline gas, LNG, LPG, Gas condensate

## Trading Hubs
- **Houston, TX** - North American hub
- **Dubai, UAE** - Middle Eastern hub
- **Singapore** - Asian hub
- **London, UK** - European hub
- **Rotterdam, Netherlands** - European refined products
- **Cushing, OK** - US storage hub

## Integration Examples

### JavaScript/Node.js
```javascript
const API_BASE = 'https://oil-trade-hub.emergent.host/api';

// Get market data
const marketData = await fetch(`${API_BASE}/market-data`);
const data = await marketData.json();

// Create listing (authenticated)
const listing = await fetch(`${API_BASE}/listings`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify(listingData)
});
```

### Python
```python
import requests

API_BASE = 'https://oil-trade-hub.emergent.host/api'
headers = {'Authorization': f'Bearer {token}'}

# Get user analytics
response = requests.get(f'{API_BASE}/analytics/user', headers=headers)
analytics = response.json()

# Create connection
connection = requests.post(
    f'{API_BASE}/connections/{listing_id}',
    headers=headers
)
```

### cURL
```bash
# Get platform statistics
curl -X GET "https://oil-trade-hub.emergent.host/api/stats"

# Create subscription (authenticated)
curl -X POST "https://oil-trade-hub.emergent.host/api/payments/create-subscription?tier=premium_basic" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Support
For API support and integration questions:
- **Email:** api-support@oil-trade-hub.com
- **Documentation:** https://oil-trade-hub.emergent.host/docs
- **Status Page:** https://status.oil-trade-hub.com

## Changelog
- **v1.0** - Initial release with core trading features
- **v1.1** - Added premium subscriptions and PayPal integration
- **v1.2** - Advanced analytics and market intelligence
- **v1.3** - Email notifications and business intelligence

---
*Last updated: January 2024*
