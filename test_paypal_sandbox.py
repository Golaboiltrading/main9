import requests

CLIENT_ID = "AeQ1AQrugD0hA4nGS3Uox37jxGSZkcgR6bKzCVCnsK9_ft9mmzP-EvLNPRbmxpF6kn8_VqbJQpMgyOWV"
CLIENT_SECRET = "EKrZyQB8Dsg1s8dAh43t6Tfm1yYZeL1Ra79A3NTH43qRVrmrhqlb0_ypSdH0VEF9ERHw2ieIPLY0Equt"

def test_paypal_sandbox():
    """Test PayPal with sandbox environment"""
    print("🧪 Testing PayPal with sandbox environment...")
    
    # PayPal sandbox OAuth endpoint
    auth_url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    
    data = "grant_type=client_credentials"
    
    try:
        response = requests.post(
            auth_url,
            headers=headers,
            data=data,
            auth=(CLIENT_ID, CLIENT_SECRET)
        )
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print(f"✅ PayPal SANDBOX authentication successful!")
            print(f"🎯 Access token received: {access_token[:20]}...")
            print(f"⏰ Token expires in: {token_data.get('expires_in')} seconds")
            print(f"🔧 Mode: SANDBOX (Safe for testing)")
            return True
        else:
            print(f"❌ PayPal sandbox authentication failed!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PayPal sandbox: {str(e)}")
        return False

if __name__ == "__main__":
    test_paypal_sandbox()
