#!/usr/bin/env python3
"""
Script to populate the vehicle database with comprehensive Chinese car brands, models, and trims.
Includes major Chinese automotive manufacturers and their vehicle lineups.
"""

import os
import sys
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import get_db
from app.db.models import VehicleBrand, VehicleModel, VehicleTrim

# Comprehensive Chinese vehicle database
CHINESE_VEHICLES = {
    "BYD": {
        "country": "China",
        "logo_url": "/images/brands/byd.png",
        "website": "https://www.byd.com",
        "description": "Build Your Dreams - Leading Chinese electric vehicle manufacturer",
        "name_fa": "بی‌وای‌دی",
        "name_cn": "比亚迪",
        "models": {
            "Tang": {
                "name_fa": "تانگ",
                "name_cn": "唐",
                "body_type": "SUV",
                "generation": "Second Generation",
                "trims": [
                    {
                        "name": "DM-i 110km",
                        "name_fa": "دی‌ام-آی 110 کیلومتر",
                        "engine_type": "2.0L Turbo Hybrid",
                        "engine_code": "BYD487ZQB",
                        "transmission": "Automatic",
                        "drivetrain": "AWD",
                        "fuel_type": "Hybrid",
                        "year_from": 2021,
                        "year_to": 2024,
                        "specifications": {
                            "power": "371 HP",
                            "torque": "675 Nm",
                            "acceleration": "4.4s 0-100km/h",
                            "fuel_consumption": "1.5L/100km"
                        }
                    },
                    {
                        "name": "EV 600km",
                        "name_fa": "برقی 600 کیلومتر",
                        "engine_type": "Electric",
                        "engine_code": "BYD-TZ220XS",
                        "transmission": "Single Speed",
                        "drivetrain": "AWD",
                        "fuel_type": "Electric",
                        "year_from": 2022,
                        "year_to": 2024,
                        "specifications": {
                            "power": "517 HP",
                            "torque": "700 Nm",
                            "range": "600 km",
                            "battery": "108.8 kWh"
                        }
                    }
                ]
            },
            "Song": {
                "name_fa": "سونگ",
                "name_cn": "宋",
                "body_type": "SUV",
                "generation": "Third Generation",
                "trims": [
                    {
                        "name": "DM-i",
                        "name_fa": "دی‌ام-آی",
                        "engine_type": "1.5L Turbo Hybrid",
                        "engine_code": "BYD487ZQA",
                        "transmission": "Automatic",
                        "drivetrain": "FWD",
                        "fuel_type": "Hybrid",
                        "year_from": 2022,
                        "year_to": 2024
                    }
                ]
            },
            "Qin": {
                "name_fa": "چین",
                "name_cn": "秦",
                "body_type": "Sedan",
                "generation": "Second Generation",
                "trims": [
                    {
                        "name": "DM-i",
                        "name_fa": "دی‌ام-آی",
                        "engine_type": "1.5L Hybrid",
                        "engine_code": "BYD371QA",
                        "transmission": "CVT",
                        "drivetrain": "FWD",
                        "fuel_type": "Hybrid",
                        "year_from": 2021,
                        "year_to": 2024
                    }
                ]
            }
        }
    },
    "Geely": {
        "country": "China",
        "logo_url": "/images/brands/geely.png",
        "website": "https://www.geely.com",
        "description": "Chinese automotive manufacturer with global presence",
        "name_fa": "جیلی",
        "name_cn": "吉利",
        "models": {
            "Coolray": {
                "name_fa": "کولری",
                "name_cn": "缤越",
                "body_type": "SUV",
                "generation": "First Generation",
                "trims": [
                    {
                        "name": "1.5T Premium",
                        "name_fa": "1.5 توربو پریمیوم",
                        "engine_type": "1.5L Turbo",
                        "engine_code": "JLH-3G15TD",
                        "transmission": "7-Speed DCT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2019,
                        "year_to": 2024
                    }
                ]
            },
            "Emgrand": {
                "name_fa": "امگرند",
                "name_cn": "帝豪",
                "body_type": "Sedan",
                "generation": "Second Generation",
                "trims": [
                    {
                        "name": "1.4T",
                        "name_fa": "1.4 توربو",
                        "engine_type": "1.4L Turbo",
                        "engine_code": "JLH-4G14T",
                        "transmission": "CVT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2018,
                        "year_to": 2024
                    }
                ]
            }
        }
    },
    "Chery": {
        "country": "China",
        "logo_url": "/images/brands/chery.png",
        "website": "https://www.chery.com",
        "description": "Leading Chinese automotive exporter",
        "name_fa": "چری",
        "name_cn": "奇瑞",
        "models": {
            "Tiggo 7": {
                "name_fa": "تیگو 7",
                "name_cn": "瑞虎7",
                "body_type": "SUV",
                "generation": "Second Generation",
                "trims": [
                    {
                        "name": "1.5T Luxury",
                        "name_fa": "1.5 توربو لاکچری",
                        "engine_type": "1.5L Turbo",
                        "engine_code": "SQRF4J15",
                        "transmission": "CVT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2020,
                        "year_to": 2024
                    }
                ]
            },
            "Arrizo 6": {
                "name_fa": "آریزو 6",
                "name_cn": "艾瑞泽6",
                "body_type": "Sedan",
                "generation": "First Generation",
                "trims": [
                    {
                        "name": "1.5T Sport",
                        "name_fa": "1.5 توربو اسپرت",
                        "engine_type": "1.5L Turbo",
                        "engine_code": "SQRF4J15",
                        "transmission": "CVT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2019,
                        "year_to": 2024
                    }
                ]
            }
        }
    },
    "Great Wall": {
        "country": "China",
        "logo_url": "/images/brands/great-wall.png",
        "website": "https://www.gwm.com.cn",
        "description": "Specializing in SUVs and pickup trucks",
        "name_fa": "دیوار بزرگ",
        "name_cn": "长城汽车",
        "models": {
            "Haval H6": {
                "name_fa": "هاوال اچ6",
                "name_cn": "哈弗H6",
                "body_type": "SUV",
                "generation": "Third Generation",
                "trims": [
                    {
                        "name": "2.0T AWD",
                        "name_fa": "2.0 توربو چهارچرخ",
                        "engine_type": "2.0L Turbo",
                        "engine_code": "GW4C20NT",
                        "transmission": "7-Speed DCT",
                        "drivetrain": "AWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2020,
                        "year_to": 2024
                    }
                ]
            },
            "Wingle 7": {
                "name_fa": "وینگل 7",
                "name_cn": "风骏7",
                "body_type": "Pickup",
                "generation": "First Generation",
                "trims": [
                    {
                        "name": "2.0T 4WD",
                        "name_fa": "2.0 توربو چهارچرخ",
                        "engine_type": "2.0L Turbo Diesel",
                        "engine_code": "GW4D20M",
                        "transmission": "6-Speed Manual",
                        "drivetrain": "4WD",
                        "fuel_type": "Diesel",
                        "year_from": 2019,
                        "year_to": 2024
                    }
                ]
            }
        }
    },
    "SAIC": {
        "country": "China",
        "logo_url": "/images/brands/saic.png",
        "website": "https://www.saicmotor.com",
        "description": "Shanghai Automotive Industry Corporation",
        "name_fa": "سایک",
        "name_cn": "上汽集团",
        "models": {
            "MG ZS": {
                "name_fa": "ام‌جی زد‌اس",
                "name_cn": "名爵ZS",
                "body_type": "SUV",
                "generation": "Second Generation",
                "trims": [
                    {
                        "name": "1.3T Trophy",
                        "name_fa": "1.3 توربو تروفی",
                        "engine_type": "1.3L Turbo",
                        "engine_code": "15E4E",
                        "transmission": "CVT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2021,
                        "year_to": 2024
                    }
                ]
            }
        }
    },
    "FAW": {
        "country": "China",
        "logo_url": "/images/brands/faw.png",
        "website": "https://www.faw.com.cn",
        "description": "First Automotive Works - China's oldest auto manufacturer",
        "name_fa": "فاو",
        "name_cn": "一汽",
        "models": {
            "Bestune T77": {
                "name_fa": "بستون تی77",
                "name_cn": "奔腾T77",
                "body_type": "SUV",
                "generation": "First Generation",
                "trims": [
                    {
                        "name": "1.2T Premium",
                        "name_fa": "1.2 توربو پریمیوم",
                        "engine_type": "1.2L Turbo",
                        "engine_code": "CA4GA12T",
                        "transmission": "7-Speed DCT",
                        "drivetrain": "FWD",
                        "fuel_type": "Gasoline",
                        "year_from": 2020,
                        "year_to": 2024
                    }
                ]
            }
        }
    }
}

def create_vehicle_brand(db: Session, brand_name: str, brand_data: dict) -> VehicleBrand:
    """Create a vehicle brand in the database."""
    
    brand = VehicleBrand(
        name=brand_name,
        name_fa=brand_data.get("name_fa"),
        name_cn=brand_data.get("name_cn"),
        logo_url=brand_data.get("logo_url"),
        country=brand_data.get("country"),
        website=brand_data.get("website"),
        description=brand_data.get("description"),
        is_active=True,
        sort_order=0
    )
    
    db.add(brand)
    db.flush()  # Get ID without committing
    return brand

def create_vehicle_model(db: Session, brand: VehicleBrand, model_name: str, model_data: dict) -> VehicleModel:
    """Create a vehicle model in the database."""
    
    model = VehicleModel(
        brand_id=brand.id,
        name=model_name,
        name_fa=model_data.get("name_fa"),
        name_cn=model_data.get("name_cn"),
        generation=model_data.get("generation"),
        body_type=model_data.get("body_type"),
        description=model_data.get("description"),
        is_active=True,
        sort_order=0
    )
    
    db.add(model)
    db.flush()
    return model

def create_vehicle_trim(db: Session, model: VehicleModel, trim_data: dict) -> VehicleTrim:
    """Create a vehicle trim in the database."""
    
    trim = VehicleTrim(
        model_id=model.id,
        name=trim_data.get("name"),
        name_fa=trim_data.get("name_fa"),
        trim_code=trim_data.get("trim_code"),
        engine_type=trim_data.get("engine_type"),
        engine_code=trim_data.get("engine_code"),
        transmission=trim_data.get("transmission"),
        drivetrain=trim_data.get("drivetrain"),
        fuel_type=trim_data.get("fuel_type"),
        year_from=trim_data.get("year_from"),
        year_to=trim_data.get("year_to"),
        specifications=trim_data.get("specifications"),
        is_active=True,
        sort_order=0
    )
    
    db.add(trim)
    db.flush()
    return trim

def populate_vehicle_database():
    """Main function to populate vehicle database."""
    print("🚗 Starting vehicle database population...")
    
    db = next(get_db())
    
    try:
        # Check if vehicles already exist
        existing_brands = db.query(VehicleBrand).count()
        if existing_brands > 0:
            print(f"⚠️  Found {existing_brands} existing brands. Use --clean flag to remove them first.")
            return
        
        total_brands = 0
        total_models = 0
        total_trims = 0
        
        for brand_name, brand_data in CHINESE_VEHICLES.items():
            print(f"📋 Creating brand: {brand_name}")
            
            # Create brand
            brand = create_vehicle_brand(db, brand_name, brand_data)
            total_brands += 1
            
            # Create models for this brand
            for model_name, model_data in brand_data.get("models", {}).items():
                print(f"  🚙 Creating model: {model_name}")
                
                model = create_vehicle_model(db, brand, model_name, model_data)
                total_models += 1
                
                # Create trims for this model
                for trim_data in model_data.get("trims", []):
                    print(f"    🔧 Creating trim: {trim_data.get('name')}")
                    
                    trim = create_vehicle_trim(db, model, trim_data)
                    total_trims += 1
        
        # Commit all changes
        db.commit()
        
        print(f"✅ Vehicle database populated successfully!")
        print(f"📊 Summary:")
        print(f"   - Brands: {total_brands}")
        print(f"   - Models: {total_models}")
        print(f"   - Trims: {total_trims}")
        
    except Exception as e:
        print(f"❌ Error during vehicle database population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def cleanup_vehicle_database():
    """Clean up existing vehicle data."""
    print("🧹 Cleaning up existing vehicle data...")
    
    db = next(get_db())
    
    try:
        # Delete in reverse order of dependencies
        trim_count = db.query(VehicleTrim).delete()
        model_count = db.query(VehicleModel).delete()
        brand_count = db.query(VehicleBrand).delete()
        
        db.commit()
        
        print(f"🗑️  Deleted:")
        print(f"   - Trims: {trim_count}")
        print(f"   - Models: {model_count}")
        print(f"   - Brands: {brand_count}")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_compatibility_data():
    """Create sample compatibility data linking parts to vehicles."""
    print("🔗 Creating vehicle-part compatibility data...")
    
    db = next(get_db())
    
    try:
        from app.db.models import Part
        
        # Get some vehicles and parts for compatibility mapping
        vehicles = db.query(VehicleTrim).limit(10).all()
        parts = db.query(Part).limit(20).all()
        
        compatibility_count = 0
        
        for vehicle in vehicles:
            # Update some parts to be compatible with this vehicle
            compatible_parts = parts[:5]  # First 5 parts compatible with each vehicle
            
            for part in compatible_parts:
                # Update part with vehicle compatibility
                part.vehicle_make = vehicle.model.brand.name
                part.vehicle_model = vehicle.model.name
                part.vehicle_trim = vehicle.name
                part.model_year_from = vehicle.year_from
                part.model_year_to = vehicle.year_to
                part.engine_code = vehicle.engine_code
                
                compatibility_count += 1
        
        db.commit()
        
        print(f"✅ Created {compatibility_count} vehicle-part compatibility records")
        
    except Exception as e:
        print(f"❌ Error creating compatibility data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def show_database_stats():
    """Show current database statistics."""
    print("📈 Vehicle Database Statistics:")
    
    db = next(get_db())
    
    try:
        brands = db.query(VehicleBrand).count()
        models = db.query(VehicleModel).count()
        trims = db.query(VehicleTrim).count()
        
        print(f"   - Brands: {brands}")
        print(f"   - Models: {models}")
        print(f"   - Trims: {trims}")
        
        # Show top brands by model count
        from sqlalchemy import func
        top_brands = db.query(
            VehicleBrand.name,
            func.count(VehicleModel.id).label('model_count')
        ).join(VehicleModel).group_by(VehicleBrand.id).order_by(
            func.count(VehicleModel.id).desc()
        ).limit(5).all()
        
        print(f"   - Top brands by model count:")
        for brand, count in top_brands:
            print(f"     {brand}: {count} models")
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate vehicle database with Chinese car data")
    parser.add_argument("--clean", action="store_true", help="Clean existing data first")
    parser.add_argument("--compatibility", action="store_true", help="Create compatibility data")
    parser.add_argument("--stats", action="store_true", help="Show database statistics")
    
    args = parser.parse_args()
    
    if args.clean:
        cleanup_vehicle_database()
    
    if args.stats:
        show_database_stats()
    elif not args.stats:
        populate_vehicle_database()
        
        if args.compatibility:
            create_compatibility_data()
    
    print("🎯 Vehicle database operation completed!")
