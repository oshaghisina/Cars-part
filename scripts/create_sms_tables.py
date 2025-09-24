#!/usr/bin/env python3
"""Create SMS-related database tables."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.database import Base
# Import all models to ensure they're registered with Base
from app.db.models import *  # This ensures all existing models are loaded
from app.models.sms_models import (
    SMSTemplate,
    SMSLog,
    StockAlert,
    SMSCampaign,
    SMSDeliveryReport
)

def create_sms_tables():
    """Create SMS-related tables in the database."""
    try:
        # Create database engine
        engine = create_engine(settings.database_url)
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ SMS tables created successfully!")
        
        # Create default SMS templates
        create_default_templates(engine)
        
        print("✅ Default SMS templates created!")
        
    except Exception as e:
        print(f"❌ Error creating SMS tables: {e}")
        return False
    
    return True

def create_default_templates(engine):
    """Create default SMS templates."""
    from sqlalchemy.orm import sessionmaker
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check if templates already exist
        existing = session.query(SMSTemplate).first()
        if existing:
            print("📝 SMS templates already exist, skipping creation")
            return
        
        # Default templates
        templates = [
            {
                "name": "order_confirmation",
                "template_type": "order",
                "content_fa": "سفارش شما با شماره {order_id} ثبت شد. مبلغ کل: {total_amount} تومان. زمان تحویل: {delivery_time}",
                "content_en": "Your order #{order_id} has been confirmed. Total amount: {total_amount} Toman. Delivery time: {delivery_time}",
                "variables": {"order_id": "Order ID", "total_amount": "Total amount", "delivery_time": "Delivery time"}
            },
            {
                "name": "order_status_update",
                "template_type": "order",
                "content_fa": "وضعیت سفارش {order_id} به {status} تغییر یافت. {additional_info}",
                "content_en": "Order #{order_id} status updated to {status}. {additional_info}",
                "variables": {"order_id": "Order ID", "status": "Status", "additional_info": "Additional information"}
            },
            {
                "name": "stock_alert",
                "template_type": "stock",
                "content_fa": "قطعه {part_name} از برند {brand} موجود شد! برای خرید: {product_url}",
                "content_en": "Part {part_name} from {brand} is now in stock! Buy now: {product_url}",
                "variables": {"part_name": "Part name", "brand": "Brand", "product_url": "Product URL"}
            },
            {
                "name": "delivery_notification",
                "template_type": "delivery",
                "content_fa": "سفارش شما {order_id} ارسال شد. کد پیگیری: {tracking_code}. زمان تحویل: {delivery_time}",
                "content_en": "Your order #{order_id} has been shipped. Tracking code: {tracking_code}. Delivery time: {delivery_time}",
                "variables": {"order_id": "Order ID", "tracking_code": "Tracking code", "delivery_time": "Delivery time"}
            },
            {
                "name": "phone_verification",
                "template_type": "verification",
                "content_fa": "کد تأیید شما: {verification_code}. این کد تا 5 دقیقه معتبر است.",
                "content_en": "Your verification code: {verification_code}. This code is valid for 5 minutes.",
                "variables": {"verification_code": "Verification code"}
            },
            {
                "name": "welcome_message",
                "template_type": "welcome",
                "content_fa": "به فروشگاه قطعات خودرو چین خوش آمدید! از خدمات ما لذت ببرید.",
                "content_en": "Welcome to China Car Parts Store! Enjoy our services.",
                "variables": {}
            }
        ]
        
        # Insert templates
        for template_data in templates:
            template = SMSTemplate(**template_data)
            session.add(template)
        
        session.commit()
        print(f"📝 Created {len(templates)} default SMS templates")
        
    except Exception as e:
        print(f"❌ Error creating default templates: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("🚀 Creating SMS database tables...")
    success = create_sms_tables()
    
    if success:
        print("🎉 SMS database setup completed successfully!")
    else:
        print("💥 SMS database setup failed!")
        sys.exit(1)
