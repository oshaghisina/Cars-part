#!/usr/bin/env python3
"""
Create a default admin user for the Chinese Auto Parts Price Bot.
"""

import sys
import os
import secrets
import string
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.db.models import User

def generate_random_password(length=12):
    """Generate a random password."""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(characters) for _ in range(length))

def create_admin_user():
    """Create a default admin user."""
    print("🔐 Creating admin user...")
    
    db = SessionLocal()
    
    try:
        # Check if admin user already exists and delete it
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("⚠️  Admin user already exists! Deleting and recreating...")
            db.delete(existing_admin)
            db.commit()
        
        # Generate random password
        password = generate_random_password()
        
        # Create admin user
        admin_user = User(
            username="admin",
            email="admin@chinacarparts.com",
            password_hash="",  # Will be set by set_password method
            salt="",  # Will be set by set_password method
            first_name="System",
            last_name="Administrator",
            role="admin",
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow(),
            last_login=None,
            login_attempts=0,
            locked_until=None
        )
        
        # Set password using User model's method
        admin_user.set_password(password)
        
        db.add(admin_user)
        db.commit()
        
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Email: admin@chinacarparts.com")
        print(f"   Password: {password}")
        print(f"   Role: admin")
        print("\n🔑 Please save this password securely!")
        print("   You can use these credentials to log into the admin panel.")
        
        return admin_user
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
