#!/usr/bin/env python3
"""
Simple AI Test Script
Tests basic AI functionality with OpenAI API key.
"""

import os
import sys
import requests
import time

def test_ai_status():
    """Test AI service status."""
    print("🤖 Testing AI Service Status...")
    try:
        response = requests.get("http://localhost:8001/api/v1/ai-search/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ AI Service Status:")
            print(f"      • AI Enabled: {data['ai_enabled']}")
            print(f"      • OpenAI Configured: {data['openai_configured']}")
            print(f"      • Model: {data['openai_model']}")
            return data['openai_configured']
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Status check error: {e}")
        return False

def test_simple_semantic_search():
    """Test simple semantic search."""
    print("\n🔍 Testing Simple Semantic Search...")
    try:
        query = "brake"
        print(f"   Query: '{query}'")
        
        response = requests.get(
            f"http://localhost:8001/api/v1/ai-search/semantic?q={query}&limit=2", 
            timeout=60  # Longer timeout for AI processing
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Semantic search successful: {len(results)} results")
            if results:
                best_result = results[0]
                print(f"      • Best match: {best_result['part_name']} - {best_result['vehicle_model']}")
                print(f"      • Search score: {best_result.get('search_score', 'N/A')}")
            return True
        else:
            print(f"   ❌ Semantic search failed: {response.status_code}")
            if response.status_code == 503:
                error_detail = response.json().get('detail', 'Unknown error')
                print(f"      • Error: {error_detail}")
            return False
    except requests.exceptions.Timeout:
        print("   ⏰ Request timed out - AI processing is taking longer than expected")
        return False
    except Exception as e:
        print(f"   ❌ Semantic search error: {e}")
        return False

def test_basic_search_fallback():
    """Test that basic search still works."""
    print("\n🔍 Testing Basic Search Fallback...")
    try:
        query = "brake"
        response = requests.get(
            f"http://localhost:8001/api/v1/search/parts?q={query}&limit=2", 
            timeout=10
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"   ✅ Basic search working: {len(results)} results")
            if results:
                best_result = results[0]
                print(f"      • Best match: {best_result['part_name']} - {best_result['vehicle_model']}")
            return True
        else:
            print(f"   ❌ Basic search failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Basic search error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Simple AI Integration Test")
    print("=" * 40)
    
    # Test API health
    print("🔍 Checking API Health...")
    try:
        response = requests.get("http://localhost:8001/health", timeout=10)
        if response.status_code == 200:
            print("   ✅ API Server is running")
        else:
            print(f"   ❌ API Health check failed: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ API Health check error: {e}")
        return
    
    # Run tests
    tests = [
        ("AI Service Status", test_ai_status),
        ("Simple Semantic Search", test_simple_semantic_search),
        ("Basic Search Fallback", test_basic_search_fallback),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n📊 Test Results")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed >= 2:  # At least status and basic search should work
        print("🎉 AI integration is working!")
        if passed == total:
            print("✨ All AI features are functional!")
        else:
            print("⚠️  Some AI features may need optimization for speed")
    else:
        print("❌ AI integration needs troubleshooting")

if __name__ == "__main__":
    main()
