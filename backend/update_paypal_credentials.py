#!/usr/bin/env python3
"""
PayPal Credentials Update Script for Oil & Gas Finder
Use this script to securely update your PayPal credentials when ready
"""

import os
import sys
from pathlib import Path

def update_paypal_credentials(client_id, client_secret, mode="live"):
    """
    Update PayPal credentials in the environment file
    
    Args:
        client_id (str): Your PayPal App Client ID
        client_secret (str): Your PayPal App Client Secret  
        mode (str): 'live' for production, 'sandbox' for testing
    """
    
    env_file_path = Path("/app/backend/.env")
    
    try:
        # Read current .env file
        with open(env_file_path, 'r') as file:
            lines = file.readlines()
        
        # Update PayPal credentials
        updated_lines = []
        credentials_updated = {
            'PAYPAL_CLIENT_ID': False,
            'PAYPAL_SECRET': False,
            'PAYPAL_MODE': False
        }
        
        for line in lines:
            if line.startswith('PAYPAL_CLIENT_ID='):
                updated_lines.append(f'PAYPAL_CLIENT_ID={client_id}\n')
                credentials_updated['PAYPAL_CLIENT_ID'] = True
            elif line.startswith('PAYPAL_SECRET='):
                updated_lines.append(f'PAYPAL_SECRET={client_secret}\n')
                credentials_updated['PAYPAL_SECRET'] = True
            elif line.startswith('PAYPAL_MODE='):
                updated_lines.append(f'PAYPAL_MODE={mode}\n')
                credentials_updated['PAYPAL_MODE'] = True
            else:
                updated_lines.append(line)
        
        # Add missing credentials if they don't exist
        if not credentials_updated['PAYPAL_CLIENT_ID']:
            updated_lines.append(f'PAYPAL_CLIENT_ID={client_id}\n')
        if not credentials_updated['PAYPAL_SECRET']:
            updated_lines.append(f'PAYPAL_SECRET={client_secret}\n')
        if not credentials_updated['PAYPAL_MODE']:
            updated_lines.append(f'PAYPAL_MODE={mode}\n')
        
        # Write updated .env file
        with open(env_file_path, 'w') as file:
            file.writelines(updated_lines)
        
        print("✅ PayPal credentials updated successfully!")
        print(f"📡 Mode: {mode}")
        print(f"🔑 Client ID: {client_id[:20]}...")
        print(f"🔐 Secret: {'*' * 20}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating PayPal credentials: {str(e)}")
        return False

def verify_credentials():
    """Verify that PayPal credentials are properly set"""
    
    env_file_path = Path("/app/backend/.env")
    
    try:
        with open(env_file_path, 'r') as file:
            content = file.read()
        
        required_vars = ['PAYPAL_CLIENT_ID', 'PAYPAL_SECRET', 'PAYPAL_MODE']
        missing_vars = []
        
        for var in required_vars:
            if var not in content or f'{var}=' not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing PayPal credentials: {', '.join(missing_vars)}")
            return False
        else:
            print("✅ All PayPal credentials are configured!")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying credentials: {str(e)}")
        return False

def create_paypal_test_script():
    """Create a test script to verify PayPal integration"""
    
    test_script = '''#!/usr/bin/env python3
"""
PayPal Integration Test Script
"""

import os
import sys
sys.path.append('/app/backend')

import asyncio
from paypal_service import PayPalService

async def test_paypal_integration():
    """Test PayPal integration with your credentials"""
    
    print("🧪 Testing PayPal Integration...")
    
    # Test subscription plan creation
    try:
        plan_id = await PayPalService.create_subscription_plan("premium_basic")
        if plan_id:
            print(f"✅ Subscription plan created: {plan_id}")
        else:
            print("❌ Failed to create subscription plan")
    except Exception as e:
        print(f"❌ Subscription plan error: {str(e)}")
    
    # Test payment creation
    try:
        payment_result = await PayPalService.create_payment("standard", "test-user-123")
        if payment_result:
            print(f"✅ Payment creation successful")
            print(f"🔗 Approval URL: {payment_result.get('approval_url', 'N/A')}")
        else:
            print("❌ Failed to create payment")
    except Exception as e:
        print(f"❌ Payment creation error: {str(e)}")
    
    print("🎯 PayPal integration test complete!")

if __name__ == "__main__":
    asyncio.run(test_paypal_integration())
'''
    
    test_file_path = Path("/app/backend/test_paypal_integration.py")
    
    try:
        with open(test_file_path, 'w') as file:
            file.write(test_script)
        
        # Make it executable
        os.chmod(test_file_path, 0o755)
        
        print("✅ PayPal test script created at: /app/backend/test_paypal_integration.py")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test script: {str(e)}")
        return False

def main():
    """Main function for interactive credential setup"""
    
    print("🚀 PayPal Credentials Setup for Oil & Gas Finder")
    print("=" * 50)
    
    # Check current status
    print("\n📋 Current Status:")
    verify_credentials()
    
    # Interactive setup
    print("\n🔧 PayPal Credential Setup")
    print("Enter your PayPal App credentials:")
    
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    mode_choice = input("Mode (1=Live/Production, 2=Sandbox/Testing) [1]: ").strip()
    mode = "live" if mode_choice != "2" else "sandbox"
    
    # Validate inputs
    if not client_id or not client_secret:
        print("❌ Both Client ID and Secret are required!")
        return
    
    if len(client_id) < 50:
        print("⚠️  Warning: Client ID seems too short. Are you sure it's correct?")
    
    if len(client_secret) < 50:
        print("⚠️  Warning: Client Secret seems too short. Are you sure it's correct?")
    
    # Update credentials
    if update_paypal_credentials(client_id, client_secret, mode):
        print("\n🎉 PayPal credentials updated successfully!")
        
        # Create test script
        create_paypal_test_script()
        
        print("\n📋 Next Steps:")
        print("1. Restart the backend server: sudo supervisorctl restart backend")
        print("2. Test the integration: python3 /app/backend/test_paypal_integration.py")
        print("3. Create your first subscription in the platform")
        print("4. Start generating revenue! 💰")
        
    else:
        print("❌ Failed to update credentials. Please try again.")

if __name__ == "__main__":
    main()
