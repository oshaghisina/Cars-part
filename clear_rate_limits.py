#!/usr/bin/env python3
"""
Script to clear rate limits for testing purposes.
"""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_db
from app.models.otp_models import RateLimit
from sqlalchemy.orm import Session

def clear_rate_limits():
    """Clear all rate limit records."""
    db = next(get_db())
    
    try:
        # Count existing rate limits
        count_before = db.query(RateLimit).count()
        print(f"Found {count_before} rate limit records")
        
        # Clear all rate limits
        db.query(RateLimit).delete()
        db.commit()
        
        count_after = db.query(RateLimit).count()
        print(f"Cleared {count_before - count_after} rate limit records")
        print("✅ Rate limits cleared successfully!")
        
    except Exception as e:
        print(f"❌ Error clearing rate limits: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    clear_rate_limits()
