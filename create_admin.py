#!/usr/bin/env python3
"""
Script to create the first admin user for Oil & Gas Finder platform
"""

import os
import sys
from pymongo import MongoClient
from datetime import datetime
import hashlib
import uuid

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = MongoClient(MONGO_URL)
db = client.oil_gas_finder
users_collection = db.users

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_admin_user():
    """Create the first admin user"""
    
    # Check if any admin users already exist
    existing_admin = users_collection.find_one({"role": {"$in": ["admin", "super_admin"]}})
    if existing_admin:
        print("❌ Admin user already exists!")
        print(f"   Email: {existing_admin['email']}")
        print(f"   Role: {existing_admin['role']}")
        return False
    
    # Admin user details
    admin_data = {
        "user_id": str(uuid.uuid4()),
        "email": "admin@oilgasfinder.com",
        "password_hash": hash_password("AdminPass123!"),
        "first_name": "Admin",
        "last_name": "User",
        "company_name": "Oil & Gas Finder",
        "country": "United States",
        "phone": "+1-555-0123",
        "trading_role": "both",
        "role": "super_admin",
        "status": "active",
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    # Insert admin user
    try:
        result = users_collection.insert_one(admin_data)
        print("✅ Super Admin user created successfully!")
        print(f"   Email: {admin_data['email']}")
        print(f"   Password: AdminPass123!")
        print(f"   Role: {admin_data['role']}")
        print(f"   User ID: {admin_data['user_id']}")
        print("\n🔒 IMPORTANT: Change the password after first login!")
        return True
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        return False

def main():
    print("🚀 Oil & Gas Finder - Admin User Creation")
    print("=" * 50)
    
    if create_admin_user():
        print("\n✅ Setup completed successfully!")
        print("   You can now login at: https://oilgasfinder.com/login")
        print("   Use the credentials above to access the Admin Panel")
    else:
        print("\n❌ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()