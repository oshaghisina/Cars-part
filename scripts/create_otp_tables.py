#!/usr/bin/env python3
"""
Script to create OTP-related database tables.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.db.database import engine, Base
from app.models.otp_models import OTPCode, PhoneVerification, RateLimit
from app.db.models import User


def create_otp_tables():
    """Create OTP-related database tables."""
    print("🔄 Creating OTP database tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ OTP tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        otp_tables = ['otp_codes', 'phone_verifications', 'rate_limits']
        for table in otp_tables:
            if table in tables:
                print(f"  ✅ {table} table created")
            else:
                print(f"  ❌ {table} table not found")
        
        print("🎉 OTP database setup completed successfully!")
        
    except Exception as e:
        print(f"❌ Error creating OTP tables: {e}")
        raise


if __name__ == "__main__":
    create_otp_tables()
