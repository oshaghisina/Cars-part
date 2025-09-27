#!/usr/bin/env python3
"""Create admin user for production deployment."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(__file__)
sys.path.insert(0, project_root)

def create_admin_user():
    """Create admin user with proper error handling."""
    try:
        from app.db.database import SessionLocal
        from app.db.models import User
        import secrets
        import string
        
        print("🔧 Creating admin user...")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if admin user already exists
            existing_admin = db.query(User).filter(User.username == "admin").first()
            if existing_admin:
                print("⚠️  Admin user already exists, removing old one...")
                db.delete(existing_admin)
                db.commit()
            
            # Generate a random password
            password_chars = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(password_chars) for _ in range(12))
            
            # Create new admin user
            admin_user = User(
                username="admin",
                email="admin@example.com",
                first_name="Admin",
                last_name="User",
                role="admin",
                is_active=True,
                is_verified=True,
                phone="+989123456789"
            )
            
            # Set password
            admin_user.set_password(password)
            
            # Add to database
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            print("✅ Admin user created successfully!")
            print(f"📧 Email: admin@example.com")
            print(f"👤 Username: admin")
            print(f"🔑 Password: {password}")
            print("\n🚨 IMPORTANT: Save this password immediately!")
            print("🔗 Login URL: http://your-server/panel/")
            
            return True
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_admin_user()
    sys.exit(0 if success else 1)