#!/usr/bin/env python3
"""
Create a comprehensive test product for PDP testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Part
from datetime import datetime

def create_test_product():
    """Create a comprehensive test product for PDP testing"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if test product already exists
        existing_part = db.query(Part).filter(Part.part_name == "Test Brake Pad - Premium").first()
        if existing_part:
            print("⚠️  Test product already exists! Updating...")
            part = existing_part
        else:
            print("🔧 Creating new test product...")
            part = Part()
        
        # Set comprehensive test data
        part.part_name = "Test Brake Pad - Premium"
        part.brand_oem = "TestBrand"
        part.vehicle_make = "BYD"
        part.vehicle_model = "F3"
        part.vehicle_trim = "Pro"
        part.oem_code = "TEST-BP-F3-001"
        part.category = "Brake System"
        part.subcategory = "Brake Pads"
        part.position = "Front"
        part.unit = "pcs"
        part.pack_size = 4
        part.status = "active"
        part.created_at = datetime.utcnow()
        part.updated_at = datetime.utcnow()
        
        if not existing_part:
            db.add(part)
        
        db.commit()
        db.refresh(part)
        
        print("✅ Test product created successfully!")
        print(f"   ID: {part.id}")
        print(f"   Name: {part.part_name}")
        print(f"   OEM Code: {part.oem_code}")
        print(f"   Category: {part.category}")
        print(f"   Status: {part.status}")
        
        return part.id
        
    except Exception as e:
        print(f"❌ Error creating test product: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    part_id = create_test_product()
    if part_id:
        print(f"\n🌐 You can now test the PDP at:")
        print(f"   http://localhost:5174/part/{part_id}")
        print(f"\n🔑 Login credentials:")
        print(f"   Email: admin@chinacarparts.com")
        print(f"   Password: kCTK39E&T#K%")
    else:
        print("❌ Failed to create test product")
        sys.exit(1)
