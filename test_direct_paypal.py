import requests
import json

def create_paypal_payment_test():
    """Test direct PayPal payment creation with your credentials"""
    
    CLIENT_ID = "AeQ1AQrugD0hA4nGS3Uox37jxGSZkcgR6bKzCVCnsK9_ft9mmzP-EvLNPRbmxpF6kn8_VqbJQpMgyOWV"
    CLIENT_SECRET = "EKrZyQB8Dsg1s8dAh43t6Tfm1yYZeL1Ra79A3NTH43qRVrmrhqlb0_ypSdH0VEF9ERHw2ieIPLY0Equt"
    
    # Step 1: Get access token
    print("🔐 Getting PayPal access token...")
    auth_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    
    auth_response = requests.post(
        auth_url,
        headers={
            "Accept": "application/json",
            "Accept-Language": "en_US",
        },
        data="grant_type=client_credentials",
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    
    if auth_response.status_code != 200:
        print(f"❌ Failed to get access token: {auth_response.text}")
        return False
    
    access_token = auth_response.json()["access_token"]
    print(f"✅ Access token obtained!")
    
    # Step 2: Create a payment
    print("💳 Creating PayPal payment...")
    payment_url = "https://api.sandbox.paypal.com/v1/payments/payment"
    
    payment_data = {
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "https://oil-trade-hub.emergent.host/payment/success",
            "cancel_url": "https://oil-trade-hub.emergent.host/payment/cancel"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": "Oil & Gas Finder Premium Basic",
                    "sku": "premium_basic",
                    "price": "10.00",
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": "10.00",
                "currency": "USD"
            },
            "description": "Monthly subscription to Oil & Gas Finder Premium Basic"
        }]
    }
    
    payment_response = requests.post(
        payment_url,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        },
        data=json.dumps(payment_data)
    )
    
    if payment_response.status_code == 201:
        payment_result = payment_response.json()
        approval_url = None
        
        for link in payment_result.get("links", []):
            if link.get("method") == "REDIRECT":
                approval_url = link.get("href")
                break
        
        print(f"✅ PayPal payment created successfully!")
        print(f"💰 Payment ID: {payment_result.get('id')}")
        print(f"🔗 Approval URL: {approval_url}")
        print(f"💳 Amount: $10.00 USD")
        print(f"📝 Description: Premium Basic Monthly Subscription")
        
        return True
    else:
        print(f"❌ Failed to create payment: {payment_response.text}")
        return False

if __name__ == "__main__":
    create_paypal_payment_test()
