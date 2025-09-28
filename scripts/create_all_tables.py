#!/usr/bin/env python3
"""
Create all database tables for testing and development.

This script creates all necessary database tables including:
- Core tables (users, parts, categories, etc.)
- Stock and pricing tables
- OTP and SMS tables
- All other required tables
"""

import sys
import os
from pathlib import Path
import logging

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.db.database import engine, Base
from app.db.models import *  # Import all models to register them
from app.models.stock_models import StockLevel, PartPrice  # Import new models

logger = logging.getLogger(__name__)

def create_all_tables():
    """Create all database tables."""
    print("🔧 Creating all database tables...")
    
    try:
        from app.core.config import settings
        print(f"📊 Database URL: {settings.database_url}")
        print(f"🌍 Environment: {settings.app_env}")
        print()
        
        # Create all tables
        print("🏗️  Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        
        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        created_tables = inspector.get_table_names()
        
        print(f"\n📋 Successfully created tables:")
        for table in sorted(created_tables):
            print(f"  ✅ {table}")
        
        print(f"\n🎉 Database setup complete! Created {len(created_tables)} tables.")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = create_all_tables()
    sys.exit(0 if success else 1)
