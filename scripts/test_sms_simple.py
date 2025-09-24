#!/usr/bin/env python3
"""Simple SMS test to isolate issues."""

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_sms_models():
    """Test SMS models directly."""
    print("🧪 Testing SMS Models Directly...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.db.database import engine
        from app.models.sms_models import SMSTemplate
        
        # Create database session
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Test querying templates
        templates = db.query(SMSTemplate).all()
        print(f"✅ Found {len(templates)} templates")
        
        for template in templates:
            print(f"   - {template.name} ({template.template_type})")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ SMS models test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sms_service():
    """Test SMS service directly."""
    print("\n🔧 Testing SMS Service Directly...")
    
    try:
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.db.database import engine
        from app.services.sms_service import SMSService
        
        # Create database session
        Session = sessionmaker(bind=engine)
        db = Session()
        
        # Initialize SMS service
        sms_service = SMSService(db)
        print("✅ SMS service initialized")
        
        # Test analytics
        analytics = sms_service.get_sms_analytics()
        print(f"✅ Analytics: {analytics}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ SMS service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test all imports."""
    print("\n📦 Testing Imports...")
    
    try:
        from app.models.sms_models import SMSTemplate, SMSLog, StockAlert
        print("✅ SMS models imported")
        
        from app.schemas.sms_schemas import SMSMessage, SMSResponse
        print("✅ SMS schemas imported")
        
        from app.services.sms_service import SMSService
        print("✅ SMS service imported")
        
        from app.api.routers.sms import router
        print("✅ SMS router imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Simple SMS Tests...")
    
    import_test = test_imports()
    models_test = test_sms_models()
    service_test = test_sms_service()
    
    if import_test and models_test and service_test:
        print("\n🎉 All simple tests passed!")
    else:
        print("\n💥 Some tests failed!")
        sys.exit(1)
