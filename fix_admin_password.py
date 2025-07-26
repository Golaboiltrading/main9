#!/usr/bin/env python3
"""
Fix admin user password hashing - convert to bcrypt
"""

import os
import sys
from pymongo import MongoClient
import bcrypt

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder
users_collection = db.users

def hash_password_bcrypt(password: str) -> str:
    """Hash password using bcrypt (matching the system)"""
    salt_rounds = 12
    salt = bcrypt.gensalt(rounds=salt_rounds)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def fix_admin_password():
    """Fix the admin user password to use bcrypt"""
    
    # Find the admin user
    admin_user = users_collection.find_one({"email": "admin@oilgasfinder.com"})
    if not admin_user:
        print("❌ Admin user not found!")
        return False
    
    # Update password to bcrypt hash
    new_password_hash = hash_password_bcrypt("AdminPass123!")
    
    try:
        result = users_collection.update_one(
            {"email": "admin@oilgasfinder.com"},
            {"$set": {"password_hash": new_password_hash}}
        )
        
        if result.modified_count > 0:
            print("✅ Admin password updated successfully!")
            print("   Email: admin@oilgasfinder.com")
            print("   Password: AdminPass123!")
            print("   Hashing: bcrypt (fixed)")
            return True
        else:
            print("❌ Failed to update admin password")
            return False
            
    except Exception as e:
        print(f"❌ Error updating admin password: {e}")
        return False

def main():
    print("🔧 Oil & Gas Finder - Fix Admin Password")
    print("=" * 50)
    
    if fix_admin_password():
        print("\n✅ Admin password fixed!")
        print("   You can now login at: https://oilgasfinder.com/login")
        print("   Email: admin@oilgasfinder.com")
        print("   Password: AdminPass123!")
    else:
        print("\n❌ Fix failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()