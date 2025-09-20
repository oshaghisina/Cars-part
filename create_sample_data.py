#!/usr/bin/env python3
"""
Create sample data for testing the Chinese Auto Parts Price Bot.
"""

import sys
import os
from datetime import datetime, date
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

from app.db.database import SessionLocal, engine
from app.db.models import Part, Price, Synonym, Lead, Order, OrderItem, Setting, User
from app.db.database import Base

def create_sample_data():
    """Create sample data for testing."""
    print("🏗️  Creating sample data...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Create sample parts
        parts_data = [
            {
                "part_name": "Front Brake Pad",
                "brand_oem": "Chery",
                "vehicle_make": "Chery",
                "vehicle_model": "Tiggo 8",
                "vehicle_trim": "Pro",
                "model_year_from": 2020,
                "model_year_to": 2024,
                "engine_code": "SQRF4J16",
                "position": "Front",
                "category": "Brake System",
                "subcategory": "Brake Pads",
                "oem_code": "CH123456",
                "alt_codes": "CH123456,ALT789,BP001",
                "dimensions_specs": '{"length": 120, "width": 80, "thickness": 15}',
                "compatibility_notes": "Compatible with X22, Tiggo 7",
                "unit": "pcs",
                "pack_size": 4,
                "status": "active"
            },
            {
                "part_name": "Oil Filter",
                "brand_oem": "JAC",
                "vehicle_make": "JAC",
                "vehicle_model": "X22",
                "model_year_from": 2019,
                "model_year_to": 2023,
                "engine_code": "HFC4GA3",
                "position": "Engine",
                "category": "Engine",
                "subcategory": "Filtration",
                "oem_code": "JAC789012",
                "alt_codes": "JAC789012,OF456",
                "dimensions_specs": '{"diameter": 75, "height": 85}',
                "compatibility_notes": "Universal fit for JAC X22",
                "unit": "pcs",
                "pack_size": 1,
                "status": "active"
            },
            {
                "part_name": "Air Filter",
                "brand_oem": "Brilliance",
                "vehicle_make": "Brilliance",
                "vehicle_model": "Arrizo 5",
                "model_year_from": 2021,
                "model_year_to": 2024,
                "engine_code": "SQRE4T15C",
                "position": "Engine",
                "category": "Engine",
                "subcategory": "Filtration",
                "oem_code": "BR345678",
                "alt_codes": "BR345678,AF789",
                "dimensions_specs": '{"length": 200, "width": 150, "height": 30}',
                "compatibility_notes": "High flow air filter",
                "unit": "pcs",
                "pack_size": 1,
                "status": "active"
            }
        ]
        
        parts = []
        for part_data in parts_data:
            part = Part(**part_data)
            db.add(part)
            parts.append(part)
        
        db.commit()
        print(f"✅ Created {len(parts)} sample parts")
        
        # Create sample prices
        prices_data = [
            # Tiggo 8 Brake Pads
            {
                "part_id": 1,
                "seller_name": "AutoParts Tehran",
                "currency": "IRR",
                "price": Decimal("450000.00"),
                "min_order_qty": 4,
                "available_qty": 50,
                "warranty": "12 months",
                "source_type": "manual",
                "valid_from": date.today(),
                "valid_to": date(2024, 12, 31),
                "note": "Original quality brake pads"
            },
            # JAC X22 Oil Filter
            {
                "part_id": 2,
                "seller_name": "JAC Service Center",
                "currency": "IRR",
                "price": Decimal("85000.00"),
                "min_order_qty": 1,
                "available_qty": 100,
                "warranty": "6 months",
                "source_type": "manual",
                "valid_from": date.today(),
                "valid_to": date(2024, 12, 31)
            },
            # Arrizo 5 Air Filter
            {
                "part_id": 3,
                "seller_name": "Brilliance Parts",
                "currency": "IRR",
                "price": Decimal("120000.00"),
                "min_order_qty": 1,
                "available_qty": 75,
                "warranty": "12 months",
                "source_type": "manual",
                "valid_from": date.today(),
                "valid_to": date(2024, 12, 31)
            }
        ]
        
        for price_data in prices_data:
            price = Price(**price_data)
            db.add(price)
        
        db.commit()
        print(f"✅ Created {len(prices_data)} sample prices")
        
        # Create sample synonyms (Persian keywords)
        synonyms_data = [
            # Tiggo 8 Brake Pads
            {"part_id": 1, "keyword": "لنت ترمز جلو", "lang": "fa", "weight": 1.0},
            {"part_id": 1, "keyword": "لنت جلو تیگو ۸", "lang": "fa", "weight": 0.9},
            {"part_id": 1, "keyword": "brake pad front", "lang": "en", "weight": 0.8},
            
            # JAC X22 Oil Filter
            {"part_id": 2, "keyword": "فیلتر روغن", "lang": "fa", "weight": 1.0},
            {"part_id": 2, "keyword": "فیلتر روغن X22", "lang": "fa", "weight": 0.9},
            {"part_id": 2, "keyword": "oil filter", "lang": "en", "weight": 0.8},
            
            # Arrizo 5 Air Filter
            {"part_id": 3, "keyword": "فیلتر هوا", "lang": "fa", "weight": 1.0},
            {"part_id": 3, "keyword": "فیلتر هوا آریزو ۵", "lang": "fa", "weight": 0.9},
            {"part_id": 3, "keyword": "air filter", "lang": "en", "weight": 0.8},
        ]
        
        for synonym_data in synonyms_data:
            synonym = Synonym(**synonym_data)
            db.add(synonym)
        
        db.commit()
        print(f"✅ Created {len(synonyms_data)} sample synonyms")
        
        # Create sample settings
        settings_data = [
            {"key": "AI_ENABLED", "value": "true"},
            {"key": "BULK_LIMIT", "value": "10"},
            {"key": "MAINTENANCE_MODE", "value": "false"},
        ]
        
        for setting_data in settings_data:
            setting = Setting(**setting_data)
            db.add(setting)
        
        db.commit()
        print(f"✅ Created {len(settings_data)} sample settings")
        
        print("\n🎉 Sample data created successfully!")
        print("\n🔍 Test queries:")
        print("   • 'لنت جلو تیگو ۸' - should find Tiggo 8 brake pads")
        print("   • 'فیلتر روغن X22' - should find JAC X22 oil filter")
        print("   • 'فیلتر هوا آریزو ۵' - should find Arrizo 5 air filter")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_sample_data()
