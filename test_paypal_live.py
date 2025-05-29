import os
import requests

# Test PayPal connection with your credentials
CLIENT_ID = "AeQ1AQrugD0hA4nGS3Uox37jxGSZkcgR6bKzCVCnsK9_ft9mmzP-EvLNPRbmxpF6kn8_VqbJQpMgyOWV"
CLIENT_SECRET = "EKrZyQB8Dsg1s8dAh43t6Tfm1yYZeL1Ra79A3NTH43qRVrmrhqlb0_ypSdH0VEF9ERHw2ieIPLY0Equt"

def test_paypal_auth():
    """Test PayPal authentication with your credentials"""
    print("🔐 Testing PayPal authentication with your live credentials...")
    
    # PayPal OAuth endpoint for live environment
    auth_url = "https://api.paypal.com/v1/oauth2/token"
    
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
            print(f"✅ PayPal authentication successful!")
            print(f"🎯 Access token received: {access_token[:20]}...")
            print(f"⏰ Token expires in: {token_data.get('expires_in')} seconds")
            return True
        else:
            print(f"❌ PayPal authentication failed!")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing PayPal: {str(e)}")
        return False

if __name__ == "__main__":
    test_paypal_auth()
