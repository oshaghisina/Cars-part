#!/usr/bin/env python3
"""Create enhanced sample data for vehicles and categories."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.models import (
    VehicleBrand, VehicleModel, VehicleTrim,
    PartCategory, Part, PartSpecification, PartImage,
    Price
)
from app.services.vehicle_service import VehicleService
from app.services.category_service import CategoryService
from app.services.parts_service import PartsService
import json


def create_vehicle_brands(db: Session):
    """Create sample vehicle brands."""
    print("🚗 Creating vehicle brands...")
    
    brands_data = [
        {
            "name": "Chery",
            "name_fa": "چری",
            "name_cn": "奇瑞",
            "country": "China",
            "website": "https://www.chery.com",
            "description": "Leading Chinese automotive manufacturer",
            "logo_url": "https://example.com/logos/chery.png",
            "sort_order": 1
        },
        {
            "name": "JAC",
            "name_fa": "جک",
            "name_cn": "江淮",
            "country": "China",
            "website": "https://www.jac.com.cn",
            "description": "Jianghuai Automobile Co., Ltd.",
            "logo_url": "https://example.com/logos/jac.png",
            "sort_order": 2
        },
        {
            "name": "Brilliance",
            "name_fa": "بریلیانس",
            "name_cn": "华晨",
            "country": "China",
            "website": "https://www.brilliance-auto.com",
            "description": "Brilliance Auto Group",
            "logo_url": "https://example.com/logos/brilliance.png",
            "sort_order": 3
        },
        {
            "name": "BYD",
            "name_fa": "بی وای دی",
            "name_cn": "比亚迪",
            "country": "China",
            "website": "https://www.byd.com",
            "description": "Build Your Dreams - Electric vehicle pioneer",
            "logo_url": "https://example.com/logos/byd.png",
            "sort_order": 4
        },
        {
            "name": "Geely",
            "name_fa": "جیلی",
            "name_cn": "吉利",
            "country": "China",
            "website": "https://www.geely.com",
            "description": "Geely Auto Group",
            "logo_url": "https://example.com/logos/geely.png",
            "sort_order": 5
        }
    ]
    
    vehicle_service = VehicleService(db)
    for brand_data in brands_data:
        brand = vehicle_service.create_brand(brand_data)
        if brand:
            print(f"✅ Created brand: {brand.name}")
        else:
            print(f"❌ Failed to create brand: {brand_data['name']}")


def create_vehicle_models(db: Session):
    """Create sample vehicle models."""
    print("🚙 Creating vehicle models...")
    
    # Get brands
    brands = db.query(VehicleBrand).all()
    brand_map = {brand.name: brand.id for brand in brands}
    
    models_data = [
        # Chery models
        {
            "brand_id": brand_map["Chery"],  # type: ignore[index]
            "name": "Tiggo 8",
            "name_fa": "تیگو 8",
            "name_cn": "瑞虎8",
            "generation": "First Generation",
            "body_type": "SUV",
            "description": "Mid-size SUV with advanced features",
            "image_url": "https://example.com/images/tiggo8.jpg",
            "sort_order": 1
        },
        {
            "brand_id": brand_map["Chery"],  # type: ignore[index]
            "name": "Tiggo 7",
            "name_fa": "تیگو 7",
            "name_cn": "瑞虎7",
            "generation": "Second Generation",
            "body_type": "SUV",
            "description": "Compact SUV with modern design",
            "image_url": "https://example.com/images/tiggo7.jpg",
            "sort_order": 2
        },
        {
            "brand_id": brand_map["Chery"],  # type: ignore[index]
            "name": "Arrizo 6",
            "name_fa": "آریزو 6",
            "name_cn": "艾瑞泽6",
            "generation": "First Generation",
            "body_type": "Sedan",
            "description": "Mid-size sedan with premium features",
            "image_url": "https://example.com/images/arrizo6.jpg",
            "sort_order": 3
        },
        
        # JAC models
        {
            "brand_id": brand_map["JAC"],  # type: ignore[index]
            "name": "S5",
            "name_fa": "اس 5",
            "name_cn": "瑞风S5",
            "generation": "Second Generation",
            "body_type": "SUV",
            "description": "Compact SUV with sporty design",
            "image_url": "https://example.com/images/jac-s5.jpg",
            "sort_order": 1
        },
        {
            "brand_id": brand_map["JAC"],  # type: ignore[index]
            "name": "iEV7S",
            "name_fa": "آی ای وی 7 اس",
            "name_cn": "iEV7S",
            "generation": "First Generation",
            "body_type": "SUV",
            "description": "Electric SUV with long range",
            "image_url": "https://example.com/images/iev7s.jpg",
            "sort_order": 2
        },
        
        # Brilliance models
        {
            "brand_id": brand_map["Brilliance"],  # type: ignore[index]
            "name": "V5",
            "name_fa": "وی 5",
            "name_cn": "中华V5",
            "generation": "First Generation",
            "body_type": "SUV",
            "description": "Compact crossover SUV",
            "image_url": "https://example.com/images/brilliance-v5.jpg",
            "sort_order": 1
        },
        {
            "brand_id": brand_map["Brilliance"],  # type: ignore[index]
            "name": "H530",
            "name_fa": "اچ 530",
            "name_cn": "中华H530",
            "generation": "First Generation",
            "body_type": "Sedan",
            "description": "Mid-size sedan with luxury features",
            "image_url": "https://example.com/images/h530.jpg",
            "sort_order": 2
        }
    ]
    
    vehicle_service = VehicleService(db)
    for model_data in models_data:
        model = vehicle_service.create_model(model_data)
        if model:
            print(f"✅ Created model: {model.name}")
        else:
            print(f"❌ Failed to create model: {model_data['name']}")


def create_vehicle_trims(db: Session):
    """Create sample vehicle trims."""
    print("🔧 Creating vehicle trims...")
    
    # Get models
    models = db.query(VehicleModel).all()
    model_map = {f"{model.brand.name} {model.name}": model.id for model in models}
    
    trims_data = [
        # Chery Tiggo 8 trims
        {
            "model_id": model_map["Chery Tiggo 8"],
            "name": "Base",
            "name_fa": "پایه",
            "trim_code": "T8-BASE",
            "engine_type": "1.5L Turbo",
            "engine_code": "SQRE4T15",
            "transmission": "Manual",
            "drivetrain": "FWD",
            "fuel_type": "Gasoline",
            "year_from": 2020,
            "year_to": 2024,
            "specifications": {
                "power": "147 HP",
                "torque": "210 Nm",
                "acceleration": "10.5s 0-100km/h"
            },
            "sort_order": 1
        },
        {
            "model_id": model_map["Chery Tiggo 8"],
            "name": "Pro",
            "name_fa": "پرو",
            "trim_code": "T8-PRO",
            "engine_type": "1.6L Turbo",
            "engine_code": "SQRF4J16",
            "transmission": "Automatic",
            "drivetrain": "FWD",
            "fuel_type": "Gasoline",
            "year_from": 2020,
            "year_to": 2024,
            "specifications": {
                "power": "197 HP",
                "torque": "290 Nm",
                "acceleration": "8.9s 0-100km/h"
            },
            "sort_order": 2
        },
        {
            "model_id": model_map["Chery Tiggo 8"],
            "name": "Premium",
            "name_fa": "پریمیوم",
            "trim_code": "T8-PREMIUM",
            "engine_type": "2.0L Turbo",
            "engine_code": "SQRF4J20",
            "transmission": "Automatic",
            "drivetrain": "AWD",
            "fuel_type": "Gasoline",
            "year_from": 2021,
            "year_to": 2024,
            "specifications": {
                "power": "254 HP",
                "torque": "390 Nm",
                "acceleration": "7.5s 0-100km/h"
            },
            "sort_order": 3
        },
        
        # JAC S5 trims
        {
            "model_id": model_map["JAC S5"],
            "name": "Comfort",
            "name_fa": "کامفورت",
            "trim_code": "S5-COM",
            "engine_type": "1.5L Turbo",
            "engine_code": "HFC4GC1.6D",
            "transmission": "Manual",
            "drivetrain": "FWD",
            "fuel_type": "Gasoline",
            "year_from": 2019,
            "year_to": 2023,
            "specifications": {
                "power": "128 HP",
                "torque": "251 Nm",
                "acceleration": "11.2s 0-100km/h"
            },
            "sort_order": 1
        },
        {
            "model_id": model_map["JAC S5"],
            "name": "Luxury",
            "name_fa": "لاکچری",
            "trim_code": "S5-LUX",
            "engine_type": "1.5L Turbo",
            "engine_code": "HFC4GC1.6D",
            "transmission": "Automatic",
            "drivetrain": "FWD",
            "fuel_type": "Gasoline",
            "year_from": 2019,
            "year_to": 2023,
            "specifications": {
                "power": "128 HP",
                "torque": "251 Nm",
                "acceleration": "11.8s 0-100km/h"
            },
            "sort_order": 2
        }
    ]
    
    vehicle_service = VehicleService(db)
    for trim_data in trims_data:
        trim = vehicle_service.create_trim(trim_data)
        if trim:
            print(f"✅ Created trim: {trim.name}")
        else:
            print(f"❌ Failed to create trim: {trim_data['name']}")


def create_part_categories(db: Session):
    """Create hierarchical part categories."""
    print("📦 Creating part categories...")
    
    categories_data = [
        # Root categories
        {
            "name": "Engine",
            "name_fa": "موتور",
            "name_cn": "发动机",
            "description": "Engine and related components",
            "icon": "engine",
            "color": "#FF6B6B",
            "sort_order": 1
        },
        {
            "name": "Transmission",
            "name_fa": "گیربکس",
            "name_cn": "变速箱",
            "description": "Transmission and drivetrain components",
            "icon": "gears",
            "color": "#4ECDC4",
            "sort_order": 2
        },
        {
            "name": "Suspension",
            "name_fa": "تعلیق",
            "name_cn": "悬挂",
            "description": "Suspension and steering components",
            "icon": "spring",
            "color": "#45B7D1",
            "sort_order": 3
        },
        {
            "name": "Brakes",
            "name_fa": "ترمز",
            "name_cn": "制动",
            "description": "Braking system components",
            "icon": "brake-disc",
            "color": "#FFA07A",
            "sort_order": 4
        },
        {
            "name": "Electrical",
            "name_fa": "برق",
            "name_cn": "电气",
            "description": "Electrical and electronic components",
            "icon": "lightning",
            "color": "#FFD93D",
            "sort_order": 5
        },
        {
            "name": "Body Parts",
            "name_fa": "بدنه",
            "name_cn": "车身",
            "description": "Body panels and exterior components",
            "icon": "car",
            "color": "#6BCF7F",
            "sort_order": 6
        },
        {
            "name": "Interior",
            "name_fa": "داخلی",
            "name_cn": "内饰",
            "description": "Interior components and accessories",
            "icon": "seat",
            "color": "#A8E6CF",
            "sort_order": 7
        },
        {
            "name": "Filters",
            "name_fa": "فیلتر",
            "name_cn": "过滤器",
            "description": "Air, oil, fuel and cabin filters",
            "icon": "filter",
            "color": "#FFB6C1",
            "sort_order": 8
        }
    ]
    
    category_service = CategoryService(db)
    
    # Create root categories
    root_categories = {}
    for cat_data in categories_data:
        category = category_service.create_category(cat_data)
        if category:
            root_categories[cat_data["name"]] = category.id
            print(f"✅ Created root category: {category.name}")
        else:
            print(f"❌ Failed to create root category: {cat_data['name']}")
    
    # Create subcategories
    subcategories_data = [
        # Engine subcategories
        {
            "parent_id": root_categories["Engine"],
            "name": "Engine Parts",
            "name_fa": "قطعات موتور",
            "name_cn": "发动机零件",
            "description": "Internal engine components",
            "icon": "cog",
            "sort_order": 1
        },
        {
            "parent_id": root_categories["Engine"],
            "name": "Cooling System",
            "name_fa": "سیستم خنک‌کننده",
            "name_cn": "冷却系统",
            "description": "Engine cooling components",
            "icon": "thermometer",
            "sort_order": 2
        },
        {
            "parent_id": root_categories["Engine"],
            "name": "Lubrication",
            "name_fa": "روغن‌کاری",
            "name_cn": "润滑",
            "description": "Engine lubrication system",
            "icon": "droplet",
            "sort_order": 3
        },
        
        # Transmission subcategories
        {
            "parent_id": root_categories["Transmission"],
            "name": "Manual Transmission",
            "name_fa": "گیربکس دستی",
            "name_cn": "手动变速箱",
            "description": "Manual transmission components",
            "icon": "manual-gear",
            "sort_order": 1
        },
        {
            "parent_id": root_categories["Transmission"],
            "name": "Automatic Transmission",
            "name_fa": "گیربکس اتوماتیک",
            "name_cn": "自动变速箱",
            "description": "Automatic transmission components",
            "icon": "auto-gear",
            "sort_order": 2
        },
        
        # Suspension subcategories
        {
            "parent_id": root_categories["Suspension"],
            "name": "Shock Absorbers",
            "name_fa": "کمک‌فنر",
            "name_cn": "减震器",
            "description": "Shock absorbers and struts",
            "icon": "spring-compressed",
            "sort_order": 1
        },
        {
            "parent_id": root_categories["Suspension"],
            "name": "Springs",
            "name_fa": "فنر",
            "name_cn": "弹簧",
            "description": "Coil springs and leaf springs",
            "icon": "spring",
            "sort_order": 2
        },
        {
            "parent_id": root_categories["Suspension"],
            "name": "Control Arms",
            "name_fa": "بازوی کنترل",
            "name_cn": "控制臂",
            "description": "Control arms and bushings",
            "icon": "arm",
            "sort_order": 3
        },
        
        # Brakes subcategories
        {
            "parent_id": root_categories["Brakes"],
            "name": "Brake Pads",
            "name_fa": "لنت ترمز",
            "name_cn": "刹车片",
            "description": "Brake pads and shoes",
            "icon": "brake-pad",
            "sort_order": 1
        },
        {
            "parent_id": root_categories["Brakes"],
            "name": "Brake Discs",
            "name_fa": "دیسک ترمز",
            "name_cn": "刹车盘",
            "description": "Brake discs and rotors",
            "icon": "brake-disc",
            "sort_order": 2
        },
        {
            "parent_id": root_categories["Brakes"],
            "name": "Brake Calipers",
            "name_fa": "کالیپر ترمز",
            "name_cn": "刹车卡钳",
            "description": "Brake calipers and cylinders",
            "icon": "caliper",
            "sort_order": 3
        }
    ]
    
    # Create subcategories
    for subcat_data in subcategories_data:
        category = category_service.create_category(subcat_data)
        if category:
            print(f"✅ Created subcategory: {category.name}")
        else:
            print(f"❌ Failed to create subcategory: {subcat_data['name']}")


def create_sample_parts(db: Session):
    """Create sample parts with enhanced data."""
    print("🔩 Creating sample parts...")
    
    # Get categories and vehicles
    # categories = db.query(PartCategory).all()  # Not used currently
    # trims = db.query(VehicleTrim).all()  # Not used currently
    
    parts_data = [
        {
            "part_name": "Front Brake Pad Set",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "vehicle_trim": "Pro",
            "model_year_from": 2020,
            "model_year_to": 2024,
            "engine_code": "SQRF4J16",
            "position": "Front",
            "category": "Brake Pads",
            "subcategory": "Front Brake Pads",
            "oem_code": "CH-BP-T8-F-001",
            "alt_codes": "CH123456,ALT789,BP001",
            "dimensions_specs": json.dumps({
                "length": "120mm",
                "width": "65mm",
                "thickness": "12mm",
                "material": "Ceramic"
            }),
            "compatibility_notes": "Compatible with Tiggo 8 Pro and Premium trims",
            "unit": "set",
            "pack_size": 4,
            "status": "active"
        },
        {
            "part_name": "Engine Oil Filter",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "vehicle_trim": "Base",
            "model_year_from": 2020,
            "model_year_to": 2024,
            "engine_code": "SQRE4T15",
            "position": "Engine",
            "category": "Filters",
            "subcategory": "Oil Filters",
            "oem_code": "CH-OF-T8-001",
            "alt_codes": "CH789012,OF002",
            "dimensions_specs": json.dumps({
                "outer_diameter": "76mm",
                "height": "90mm",
                "thread_size": "M20x1.5",
                "bypass_pressure": "12-15 PSI"
            }),
            "compatibility_notes": "For 1.5L Turbo engine",
            "unit": "pcs",
            "pack_size": 1,
            "status": "active"
        },
        {
            "part_name": "Front Shock Absorber",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "vehicle_trim": "Premium",
            "model_year_from": 2021,
            "model_year_to": 2024,
            "engine_code": "SQRF4J20",
            "position": "Front-Left",
            "category": "Shock Absorbers",
            "subcategory": "Front Shock Absorbers",
            "oem_code": "CH-SA-T8-FL-001",
            "alt_codes": "CH345678,SA003",
            "dimensions_specs": json.dumps({
                "compressed_length": "350mm",
                "extended_length": "520mm",
                "stroke": "170mm",
                "mounting_type": "Top Mount"
            }),
            "compatibility_notes": "For AWD Premium trim only",
            "unit": "pcs",
            "pack_size": 1,
            "status": "active"
        },
        {
            "part_name": "Air Filter Element",
            "brand_oem": "JAC",
            "vehicle_make": "JAC",
            "vehicle_model": "S5",
            "vehicle_trim": "Comfort",
            "model_year_from": 2019,
            "model_year_to": 2023,
            "engine_code": "HFC4GC1.6D",
            "position": "Engine Bay",
            "category": "Filters",
            "subcategory": "Air Filters",
            "oem_code": "JAC-AF-S5-001",
            "alt_codes": "JAC456789,AF004",
            "dimensions_specs": json.dumps({
                "length": "280mm",
                "width": "200mm",
                "height": "45mm",
                "filtration_efficiency": "99.5%"
            }),
            "compatibility_notes": "High efficiency air filter",
            "unit": "pcs",
            "pack_size": 1,
            "status": "active"
        }
    ]
    
    parts_service = PartsService(db)
    for part_data in parts_data:
        part = parts_service.create_part(part_data)
        if part:
            print(f"✅ Created part: {part.part_name}")
            
            # Add specifications
            if part.part_name == "Front Brake Pad Set":  # type: ignore[comparison-overlap]
                specs = [
                    {"spec_name": "Material", "spec_value": "Ceramic", "spec_type": "text", "is_required": True},
                    {"spec_name": "Friction Coefficient", "spec_value": "0.45", "spec_unit": "", "spec_type": "number"},
                    {"spec_name": "Operating Temperature", "spec_value": "-40 to 600", "spec_unit": "°C", "spec_type": "text"}
                ]
            elif part.part_name == "Engine Oil Filter":  # type: ignore[comparison-overlap]
                specs = [
                    {"spec_name": "Filtration Rating", "spec_value": "10 micron", "spec_type": "text", "is_required": True},
                    {"spec_name": "Flow Rate", "spec_value": "25", "spec_unit": "L/min", "spec_type": "number"},
                    {"spec_name": "Capacity", "spec_value": "0.5", "spec_unit": "L", "spec_type": "number"}
                ]
            else:
                specs = []
            
            for spec_data in specs:
                spec = PartSpecification(
                    part_id=part.id,
                    **spec_data
                )
                db.add(spec)
            
            # Add images
            images = [
                {"image_url": f"https://example.com/images/{part.oem_code}_main.jpg", "image_type": "main", "alt_text": part.part_name},
                {"image_url": f"https://example.com/images/{part.oem_code}_detail.jpg", "image_type": "detail", "alt_text": f"{part.part_name} detail view"}
            ]
            
            for img_data in images:
                img = PartImage(
                    part_id=part.id,
                    **img_data
                )
                db.add(img)
            
            db.commit()
        else:
            print(f"❌ Failed to create part: {part_data['part_name']}")


def create_sample_prices(db: Session):
    """Create sample prices for parts."""
    print("💰 Creating sample prices...")
    
    parts = db.query(Part).all()
    
    for part in parts[:2]:  # Add prices for first 2 parts
        prices_data = [
            {
                "part_id": part.id,
                "seller_name": "AutoParts Tehran",
                "seller_url": "https://autoparts-tehran.com",
                "currency": "IRR",
                "price": 450000.00,
                "min_order_qty": 1,
                "available_qty": 50,
                "warranty": "12 months",
                "source_type": "manual",
                "note": "Original OEM quality"
            },
            {
                "part_id": part.id,
                "seller_name": "China Parts Direct",
                "seller_url": "https://chinapartsdirect.com",
                "currency": "IRR",
                "price": 380000.00,
                "min_order_qty": 4,
                "available_qty": 100,
                "warranty": "6 months",
                "source_type": "manual",
                "note": "Aftermarket equivalent"
            }
        ]
        
        for price_data in prices_data:
            price = Price(**price_data)
            db.add(price)
    
    db.commit()
    print("✅ Created sample prices")


def main():
    """Main function to create all sample data."""
    print("🚀 Creating enhanced sample data...")
    
    # Create database tables
    from app.db.models import Base
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create sample data
        create_vehicle_brands(db)
        create_vehicle_models(db)
        create_vehicle_trims(db)
        create_part_categories(db)
        create_sample_parts(db)
        create_sample_prices(db)
        
        print("\n🎉 Enhanced sample data created successfully!")
        print("\n📊 Summary:")
        print(f"✅ Vehicle Brands: {db.query(VehicleBrand).count()}")
        print(f"✅ Vehicle Models: {db.query(VehicleModel).count()}")
        print(f"✅ Vehicle Trims: {db.query(VehicleTrim).count()}")
        print(f"✅ Part Categories: {db.query(PartCategory).count()}")
        print(f"✅ Parts: {db.query(Part).count()}")
        print(f"✅ Part Specifications: {db.query(PartSpecification).count()}")
        print(f"✅ Part Images: {db.query(PartImage).count()}")
        print(f"✅ Prices: {db.query(Price).count()}")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    main()
