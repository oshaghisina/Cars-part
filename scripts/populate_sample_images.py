#!/usr/bin/env python3
"""
Script to populate the database with sample product images.
Creates realistic image entries for existing parts in the database.
"""

import os
import sys
import requests
import urllib.parse
from pathlib import Path
from sqlalchemy.orm import Session

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import get_db
from app.db.models import Part, PartImage

# Sample automotive part images from placeholder services
SAMPLE_IMAGES = {
    "brake-pads": [
        "https://picsum.photos/800/600?random=1",
        "https://picsum.photos/800/600?random=2",
        "https://picsum.photos/800/600?random=3"
    ],
    "air-filter": [
        "https://picsum.photos/800/600?random=4",
        "https://picsum.photos/800/600?random=5"
    ],
    "oil-filter": [
        "https://picsum.photos/800/600?random=6",
        "https://picsum.photos/800/600?random=7"
    ],
    "spark-plug": [
        "https://picsum.photos/800/600?random=8",
        "https://picsum.photos/800/600?random=9",
        "https://picsum.photos/800/600?random=10"
    ],
    "alternator": [
        "https://picsum.photos/800/600?random=11",
        "https://picsum.photos/800/600?random=12"
    ],
    "suspension": [
        "https://picsum.photos/800/600?random=13",
        "https://picsum.photos/800/600?random=14",
        "https://picsum.photos/800/600?random=15"
    ],
    "radiator": [
        "https://picsum.photos/800/600?random=16",
        "https://picsum.photos/800/600?random=17"
    ],
    "headlight": [
        "https://picsum.photos/800/600?random=18",
        "https://picsum.photos/800/600?random=19",
        "https://picsum.photos/800/600?random=20"
    ]
}

# Fallback generic automotive images
GENERIC_IMAGES = [
    "https://picsum.photos/800/600?random=21",
    "https://picsum.photos/800/600?random=22",
    "https://picsum.photos/800/600?random=23",
    "https://picsum.photos/800/600?random=24",
    "https://picsum.photos/800/600?random=25"
]

def get_category_images(category: str) -> list:
    """Get sample images for a specific category."""
    category_lower = category.lower()
    
    for key in SAMPLE_IMAGES:
        if key in category_lower or category_lower in key:
            return SAMPLE_IMAGES[key]
    
    # Return generic images if no specific category match
    return GENERIC_IMAGES[:2]

def create_part_images(db: Session, part: Part, image_urls: list):
    """Create PartImage records for a part."""
    created_images = []
    
    for index, url in enumerate(image_urls):
        # Determine image type based on index
        if index == 0:
            image_type = "main"
        elif index == 1:
            image_type = "detail"
        elif index == 2:
            image_type = "installation"
        else:
            image_type = "gallery"
        
        # Create PartImage record
        part_image = PartImage(
            part_id=part.id,
            image_url=url,
            image_type=image_type,
            alt_text=f"{part.part_name} - {image_type} view",
            sort_order=index,
            is_active=True
        )
        
        db.add(part_image)
        created_images.append(part_image)
    
    return created_images

def populate_sample_images():
    """Main function to populate sample images."""
    print("🖼️  Starting sample image population...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Get all active parts
        parts = db.query(Part).filter(Part.status == "active").all()
        
        if not parts:
            print("❌ No active parts found in database")
            return
        
        print(f"📊 Found {len(parts)} active parts")
        
        total_images_created = 0
        
        for part in parts:
            # Check if part already has images
            existing_images = db.query(PartImage).filter(PartImage.part_id == part.id).count()
            
            if existing_images > 0:
                print(f"⏭️  Skipping part {part.id} ({part.part_name}) - already has {existing_images} images")
                continue
            
            # Get sample images for this part's category
            image_urls = get_category_images(part.category or "generic")
            
            # Create image records
            created_images = create_part_images(db, part, image_urls)
            total_images_created += len(created_images)
            
            print(f"✅ Created {len(created_images)} images for part {part.id} ({part.part_name})")
        
        # Commit all changes
        db.commit()
        
        print(f"🎉 Successfully created {total_images_created} sample images!")
        
        # Summary statistics
        total_parts_with_images = db.query(Part).join(PartImage).distinct(Part.id).count()
        total_images = db.query(PartImage).count()
        
        print(f"📈 Summary:")
        print(f"   - Parts with images: {total_parts_with_images}")
        print(f"   - Total images: {total_images}")
        
    except Exception as e:
        print(f"❌ Error during image population: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_360_images():
    """Create sample 360-degree images for showcase parts."""
    print("🔄 Creating sample 360° images...")
    
    db = next(get_db())
    
    try:
        # Find parts suitable for 360° view (typically major components)
        suitable_parts = db.query(Part).filter(
            Part.status == "active",
            Part.category.in_(["alternator", "radiator", "headlight", "suspension"])
        ).limit(5).all()
        
        for part in suitable_parts:
            # Create 8 frames for 360° view
            for frame in range(8):
                angle = frame * 45  # 45-degree increments
                
                part_image = PartImage(
                    part_id=part.id,
                    image_url=f"https://picsum.photos/400/400?random={100 + frame}&t={part.id}",
                    image_type="360",
                    alt_text=f"{part.part_name} - 360° view frame {frame + 1}",
                    sort_order=frame,
                    is_active=True
                )
                
                db.add(part_image)
            
            print(f"🔄 Created 360° images for part {part.id} ({part.part_name})")
        
        db.commit()
        print("✅ 360° images created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating 360° images: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def create_sample_installation_images():
    """Create sample installation guide images."""
    print("🔧 Creating sample installation images...")
    
    db = next(get_db())
    
    try:
        # Get parts that commonly have installation guides
        installation_parts = db.query(Part).filter(
            Part.status == "active",
            Part.category.in_(["brake-pads", "air-filter", "oil-filter", "spark-plug"])
        ).limit(10).all()
        
        for part in installation_parts:
            # Create 3-4 installation step images
            for step in range(1, 5):
                part_image = PartImage(
                    part_id=part.id,
                    image_url=f"https://picsum.photos/600/400?random={200 + step}&t={part.id}",
                    image_type="installation",
                    alt_text=f"{part.part_name} - Installation step {step}",
                    sort_order=step + 10,  # Offset to not conflict with main images
                    is_active=True
                )
                
                db.add(part_image)
            
            print(f"🔧 Created installation images for part {part.id} ({part.part_name})")
        
        db.commit()
        print("✅ Installation images created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating installation images: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def cleanup_existing_images():
    """Clean up existing sample images (optional)."""
    print("🧹 Cleaning up existing sample images...")
    
    db = next(get_db())
    
    try:
        # Delete all existing PartImage records
        deleted_count = db.query(PartImage).delete()
        db.commit()
        
        print(f"🗑️  Deleted {deleted_count} existing image records")
        
    except Exception as e:
        print(f"❌ Error during cleanup: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate database with sample product images")
    parser.add_argument("--clean", action="store_true", help="Clean existing images first")
    parser.add_argument("--basic", action="store_true", help="Create basic images only")
    parser.add_argument("--360", action="store_true", help="Create 360° images")
    parser.add_argument("--installation", action="store_true", help="Create installation images")
    parser.add_argument("--all", action="store_true", help="Create all types of images")
    
    args = parser.parse_args()
    
    if args.clean:
        cleanup_existing_images()
    
    if args.basic or args.all or not any([args.basic, args.360, args.installation]):
        populate_sample_images()
    
    if args.360 or args.all:
        create_sample_360_images()
    
    if args.installation or args.all:
        create_sample_installation_images()
    
    print("🎯 Sample image population completed!")
