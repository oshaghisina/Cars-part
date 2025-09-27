#!/usr/bin/env python3
"""
Idempotent migration script to create stock_levels and normalize prices tables.
Safe to run on production - checks for existing tables before creating.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from app.db.database import engine, Base
from app.models.stock_models import StockLevel, Price
from app.db.models import Part, PartCategory

def create_stock_pricing_tables():
    """Create stock_levels and normalized prices tables if they don't exist."""
    print("🔧 Creating stock and pricing tables...")
    
    try:
        from sqlalchemy import inspect, text
        from app.core.config import settings
        
        print(f"📊 Database URL: {settings.database_url}")
        print(f"🌍 Environment: {settings.app_env}")
        print()
        
        # Check if tables already exist
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        print("🔍 Checking existing tables...")
        required_tables = ['stock_levels', 'prices_new']
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if not missing_tables:
            print("✅ All required tables already exist!")
            return True
        
        print(f"📋 Missing tables: {', '.join(missing_tables)}")
        print()
        
        # Create missing tables
        print("🏗️  Creating missing tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Stock and pricing tables created successfully!")
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        created_tables = [table for table in required_tables if table in new_tables]
        
        print(f"\n📋 Successfully created/verified tables:")
        for table in created_tables:
            print(f"  ✅ {table}")
        
        # Create stock levels for existing parts if stock_levels was created
        if 'stock_levels' in created_tables:
            print("\n📦 Creating stock levels for existing parts...")
            with engine.connect() as conn:
                # Get all existing parts
                result = conn.execute(text("SELECT id FROM parts"))
                part_ids = [row[0] for row in result]
                
                if part_ids:
                    # Insert default stock levels for existing parts
                    stock_inserts = []
                    for part_id in part_ids:
                        stock_inserts.append({
                            'part_id': part_id,
                            'current_stock': 0,
                            'reserved_quantity': 0,
                            'min_stock_level': 0
                        })
                    
                    # Bulk insert
                    conn.execute(text("""
                        INSERT INTO stock_levels (part_id, current_stock, reserved_quantity, min_stock_level, created_at, updated_at)
                        VALUES (:part_id, :current_stock, :reserved_quantity, :min_stock_level, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """), stock_inserts)
                    conn.commit()
                    
                    print(f"  ✅ Created stock levels for {len(part_ids)} existing parts")
                else:
                    print("  ℹ️  No existing parts found to create stock levels for")
        
        print("\n🎯 Next steps:")
        print("  1. Test stock management endpoints")
        print("  2. Test pricing endpoints")
        print("  3. Verify admin panel integration")
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = create_stock_pricing_tables()
    sys.exit(0 if success else 1)
