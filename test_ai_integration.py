#!/usr/bin/env python3
"""
AI Integration Test Script
Tests OpenAI integration and AI-enhanced search functionality.
"""

import os
import sys
import requests
from datetime import datetime

# Add app directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'app')))

def test_ai_status():
    """Test AI service status endpoint."""
    print("🤖 Testing AI Service Status...")
    try:
        response = requests.get("http://localhost:8001/api/v1/ai-search/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ AI Service Status:")
            print(f"      • AI Enabled: {data['ai_enabled']}")
            print(f"      • OpenAI Configured: {data['openai_configured']}")
            print(f"      • Model: {data['openai_model']}")
            print(f"      • Embedding Model: {data['embedding_model']}")
            return data['openai_configured']
        else:
            print(f"   ❌ AI Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ AI Status check error: {e}")
        return False

def test_semantic_search():
    """Test semantic search functionality."""
    print("\n🔍 Testing Semantic Search...")
    try:
        test_queries = [
            "لنت ترمز جلو تیگو ۸",
            "فیلتر روغن X22",
            "brake pad front Chery Tiggo 8"
        ]
        
        for query in test_queries:
            response = requests.get(f"http://localhost:8001/api/v1/ai-search/semantic?q={query}&limit=3", timeout=15)
            if response.status_code == 200:
                results = response.json()
                print(f"   ✅ Semantic search '{query}': {len(results)} results")
                if results:
                    best_result = results[0]
                    print(f"      • Best match: {best_result['part_name']} - {best_result['vehicle_model']}")
                    print(f"      • Search score: {best_result.get('search_score', 'N/A')}")
                    print(f"      • Match type: {best_result.get('match_type', 'N/A')}")
            else:
                print(f"   ❌ Semantic search '{query}' failed: {response.status_code}")
                if response.status_code == 503:
                    print(f"      • Error: {response.json().get('detail', 'Unknown error')}")
                    return False
    except Exception as e:
        print(f"   ❌ Semantic search error: {e}")
        return False
    
    return True

def test_intelligent_search():
    """Test intelligent search with query analysis."""
    print("\n🧠 Testing Intelligent Search...")
    try:
        test_queries = [
            "من دنبال لنت ترمز جلو برای تیگو ۸ هستم",
            "I need brake pads for Chery Tiggo 8 front",
            "فیلتر هوا برای X22 می‌خواهم"
        ]
        
        for query in test_queries:
            response = requests.get(f"http://localhost:8001/api/v1/ai-search/intelligent?q={query}&limit=2", timeout=20)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Intelligent search '{query}':")
                print(f"      • Success: {data['success']}")
                print(f"      • Parts found: {len(data['parts'])}")
                print(f"      • Search type: {data['search_type']}")
                
                if data.get('query_analysis'):
                    analysis = data['query_analysis']
                    print(f"      • Query analysis:")
                    print(f"        - Intent: {analysis.get('intent', 'N/A')}")
                    print(f"        - Car brand: {analysis.get('car_brand', 'N/A')}")
                    print(f"        - Car model: {analysis.get('car_model', 'N/A')}")
                    print(f"        - Part type: {analysis.get('part_type', 'N/A')}")
                    print(f"        - Language: {analysis.get('language', 'N/A')}")
                
                if data.get('suggestions'):
                    print(f"      • AI Suggestions: {len(data['suggestions'])} suggestions")
                    for i, suggestion in enumerate(data['suggestions'][:2], 1):
                        print(f"        {i}. {suggestion}")
                
                if data['parts']:
                    best_part = data['parts'][0]
                    print(f"      • Best result: {best_part['part_name']} - {best_part['vehicle_model']}")
            else:
                print(f"   ❌ Intelligent search '{query}' failed: {response.status_code}")
                if response.status_code == 503:
                    print(f"      • Error: {response.json().get('detail', 'Unknown error')}")
                    return False
    except Exception as e:
        print(f"   ❌ Intelligent search error: {e}")
        return False
    
    return True

def test_bulk_intelligent_search():
    """Test bulk intelligent search."""
    print("\n📦 Testing Bulk Intelligent Search...")
    try:
        bulk_data = {
            "queries": [
                "لنت جلو تیگو ۸",
                "فیلتر روغن X22",
                "فیلتر هوا H330"
            ],
            "limit_per_query": 2
        }
        
        response = requests.post("http://localhost:8001/api/v1/ai-search/intelligent/bulk", json=bulk_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            print(f"   ✅ Bulk intelligent search: {len(results)} queries processed")
            
            for i, result in enumerate(results, 1):
                print(f"      Query {i}: '{result['query']}'")
                print(f"        • Success: {result['success']}")
                print(f"        • Parts found: {len(result['parts'])}")
                print(f"        • Search type: {result['search_type']}")
                
                if result.get('suggestions'):
                    print(f"        • Suggestions: {len(result['suggestions'])}")
        else:
            print(f"   ❌ Bulk intelligent search failed: {response.status_code}")
            if response.status_code == 503:
                print(f"      • Error: {response.json().get('detail', 'Unknown error')}")
                return False
    except Exception as e:
        print(f"   ❌ Bulk intelligent search error: {e}")
        return False
    
    return True

def test_part_recommendations():
    """Test part recommendations."""
    print("\n💡 Testing Part Recommendations...")
    try:
        # First get a part ID from the parts list
        parts_response = requests.get("http://localhost:8001/api/v1/parts/", timeout=10)
        if parts_response.status_code == 200:
            parts = parts_response.json()
            if parts:
                part_id = parts[0]['id']
                
                response = requests.get(f"http://localhost:8001/api/v1/ai-search/recommendations/{part_id}?limit=3", timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data['recommendations']
                    print(f"   ✅ Part recommendations for part ID {part_id}: {len(recommendations)} recommendations")
                    
                    for i, rec in enumerate(recommendations, 1):
                        print(f"      {i}. {rec['part_name']} - {rec['vehicle_model']} (Score: {rec.get('search_score', 'N/A')})")
                else:
                    print(f"   ❌ Part recommendations failed: {response.status_code}")
                    if response.status_code == 503:
                        print(f"      • Error: {response.json().get('detail', 'Unknown error')}")
                        return False
            else:
                print("   ⚠️  No parts available for recommendations test")
        else:
            print(f"   ❌ Failed to get parts list: {parts_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Part recommendations error: {e}")
        return False
    
    return True

def test_ai_vs_basic_search():
    """Compare AI search vs basic search."""
    print("\n⚖️  Comparing AI Search vs Basic Search...")
    try:
        test_query = "لنت ترمز جلو تیگو ۸"
        
        # Basic search
        basic_response = requests.get(f"http://localhost:8001/api/v1/search/parts?q={test_query}&limit=3", timeout=10)
        
        # AI search
        ai_response = requests.get(f"http://localhost:8001/api/v1/ai-search/semantic?q={test_query}&limit=3", timeout=15)
        
        if basic_response.status_code == 200 and ai_response.status_code == 200:
            basic_results = basic_response.json()
            ai_results = ai_response.json()
            
            print(f"   Query: '{test_query}'")
            print(f"   • Basic search: {len(basic_results)} results")
            print(f"   • AI search: {len(ai_results)} results")
            
            if basic_results and ai_results:
                print(f"   • Basic best match: {basic_results[0]['part_name']} - {basic_results[0]['vehicle_model']}")
                print(f"   • AI best match: {ai_results[0]['part_name']} - {ai_results[0]['vehicle_model']}")
                
                basic_score = basic_results[0].get('search_score', 0)
                ai_score = ai_results[0].get('search_score', 0)
                print(f"   • Basic score: {basic_score}")
                print(f"   • AI score: {ai_score}")
                
                if ai_score > basic_score:
                    print(f"   🎯 AI search provides better results!")
                elif basic_score > ai_score:
                    print(f"   📊 Basic search provides better results")
                else:
                    print(f"   🤝 Both searches provide similar results")
        else:
            print(f"   ❌ Comparison failed - Basic: {basic_response.status_code}, AI: {ai_response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Comparison error: {e}")
        return False
    
    return True

def main():
    """Main test function."""
    print("🧪 AI Integration Test Suite")
    print("=" * 50)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check API health first
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
    
    # Run all tests
    tests = [
        ("AI Service Status", test_ai_status),
        ("Semantic Search", test_semantic_search),
        ("Intelligent Search", test_intelligent_search),
        ("Bulk Intelligent Search", test_bulk_intelligent_search),
        ("Part Recommendations", test_part_recommendations),
        ("AI vs Basic Search Comparison", test_ai_vs_basic_search),
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
    print("📊 AI Integration Test Results")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print()
    print(f"🎯 Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All AI integration tests passed!")
        print("\n✨ AI-enhanced search is working perfectly!")
        print("🚀 Your system now has intelligent search capabilities!")
    else:
        print("⚠️  Some AI tests failed.")
        print("\n📋 Troubleshooting Tips:")
        print("1. Make sure OpenAI API key is set in .env file")
        print("2. Check internet connection for OpenAI API access")
        print("3. Verify API key has sufficient credits")
        print("4. Check OpenAI API status at https://status.openai.com/")
    
    print("\n🔧 Configuration Required:")
    print("Add to your .env file:")
    print("OPENAI_API_KEY=your_actual_openai_api_key_here")
    print("AI_ENABLED=true")

if __name__ == "__main__":
    main()
