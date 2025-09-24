#!/usr/bin/env python3
"""
Create a comprehensive test product with all PDP features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Part
from datetime import datetime

def create_comprehensive_test_product():
    """Create a comprehensive test product with all PDP features"""
    
    # Get database session
    db = next(get_db())
    
    try:
        # Check if comprehensive test product already exists
        existing_part = db.query(Part).filter(Part.part_name == "لنت ترمز جلو - سرامیک").first()
        if existing_part:
            print("⚠️  Comprehensive test product already exists! Updating...")
            part = existing_part
        else:
            print("🔧 Creating comprehensive test product...")
            part = Part()
        
        # Set comprehensive test data with Persian names
        part.part_name = "لنت ترمز جلو - سرامیک"
        part.brand_oem = "OEM Premium"
        part.vehicle_make = "BYD"
        part.vehicle_model = "F3"
        part.vehicle_trim = "Pro"
        part.oem_code = "BP-F3-2020-PREMIUM"
        part.category = "سیستم ترمز"
        part.subcategory = "لنت ترمز"
        part.position = "جلو"
        part.unit = "عدد"
        part.pack_size = 4
        part.status = "active"
        part.created_at = datetime.utcnow()
        part.updated_at = datetime.utcnow()
        
        if not existing_part:
            db.add(part)
        
        db.commit()
        db.refresh(part)
        
        print("✅ Comprehensive test product created successfully!")
        print(f"   ID: {part.id}")
        print(f"   Name: {part.part_name}")
        print(f"   OEM Code: {part.oem_code}")
        print(f"   Category: {part.category}")
        print(f"   Status: {part.status}")
        
        return part.id
        
    except Exception as e:
        print(f"❌ Error creating comprehensive test product: {e}")
        db.rollback()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    part_id = create_comprehensive_test_product()
    if part_id:
        print(f"\n🌐 You can now test the PDP at:")
        print(f"   http://localhost:5174/part/{part_id}")
        print(f"\n🔑 Login credentials:")
        print(f"   Email: admin@chinacarparts.com")
        print(f"   Password: kCTK39E&T#K%")
        print(f"\n📱 Test Features:")
        print(f"   ✅ Persian/Farsi UI with RTL layout")
        print(f"   ✅ Fitment Bar with VIN input")
        print(f"   ✅ Buy Box with pricing and stock")
        print(f"   ✅ Media Gallery with zoom")
        print(f"   ✅ Product specifications")
        print(f"   ✅ OEM cross-references")
        print(f"   ✅ Authentication system")
        print(f"   ✅ Analytics tracking")
        print(f"   ✅ Test component for debugging")
    else:
        print("❌ Failed to create comprehensive test product")
        sys.exit(1)
