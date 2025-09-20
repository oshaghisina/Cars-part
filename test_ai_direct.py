#!/usr/bin/env python3
"""
Direct AI Test Script
Tests AI service directly without HTTP requests.
"""

import os
import sys
from datetime import datetime

# Add app directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

def test_ai_service_direct():
    """Test AI service directly."""
    print("🤖 Testing AI Service Directly...")
    
    try:
        from app.services.ai_service import AIService
        from app.db.database import SessionLocal
        
        # Create database session
        db = SessionLocal()
        
        # Create AI service
        ai_service = AIService(db)
        
        # Test availability
        is_available = ai_service.is_available()
        print(f"   ✅ AI Service Available: {is_available}")
        
        if is_available:
            print("   🧠 Testing OpenAI API connection...")
            
            # Test with a simple query
            test_query = "brake pad"
            print(f"   Query: '{test_query}'")
            
            try:
                # Test semantic search
                results = ai_service.semantic_search(test_query, limit=2)
                print(f"   ✅ Semantic search successful: {len(results)} results")
                
                if results:
                    best_result = results[0]
                    print(f"      • Best match: {best_result['part_name']} - {best_result['vehicle_model']}")
                    print(f"      • Search score: {best_result.get('search_score', 'N/A')}")
                    print(f"      • Match type: {best_result.get('match_type', 'N/A')}")
                
                return True
                
            except Exception as e:
                print(f"   ❌ Semantic search error: {e}")
                return False
        else:
            print("   ⚠️  AI Service not available - checking configuration...")
            from app.core.config import settings
            print(f"      • AI Enabled: {settings.ai_enabled}")
            print(f"      • OpenAI API Key Set: {bool(settings.openai_api_key)}")
            print(f"      • OpenAI Model: {settings.openai_model}")
            return False
            
    except Exception as e:
        print(f"   ❌ AI Service test error: {e}")
        return False
    finally:
        db.close()

def test_openai_connection():
    """Test OpenAI connection directly."""
    print("\n🔗 Testing OpenAI Connection...")
    
    try:
        import openai
        from app.core.config import settings
        
        if not settings.openai_api_key:
            print("   ❌ OpenAI API key not configured")
            return False
        
        # Set API key
        openai.api_key = settings.openai_api_key
        client = openai.OpenAI(api_key=settings.openai_api_key)
        
        print("   🧪 Testing simple OpenAI API call...")
        
        # Test with a simple completion
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[{"role": "user", "content": "Hello, this is a test. Please respond with 'AI connection successful!'"}],
            max_tokens=50,
            temperature=0.1
        )
        
        result = response.choices[0].message.content
        print(f"   ✅ OpenAI API Response: {result}")
        
        if "successful" in result.lower():
            print("   🎉 OpenAI connection is working!")
            return True
        else:
            print("   ⚠️  OpenAI responded but with unexpected content")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenAI connection error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Direct AI Integration Test")
    print("=" * 40)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Run tests
    tests = [
        ("AI Service Direct Test", test_ai_service_direct),
        ("OpenAI Connection Test", test_openai_connection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
            print()
    
    # Summary
    print("📊 Test Results")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 AI integration is working perfectly!")
        print("✨ Your OpenAI API key is configured and functional!")
    elif passed > 0:
        print("⚠️  Partial AI integration - some features working")
    else:
        print("❌ AI integration needs troubleshooting")
        print("\n🔧 Troubleshooting Tips:")
        print("1. Verify OpenAI API key is correct")
        print("2. Check internet connection")
        print("3. Verify OpenAI account has credits")
        print("4. Check OpenAI API status")

if __name__ == "__main__":
    main()
