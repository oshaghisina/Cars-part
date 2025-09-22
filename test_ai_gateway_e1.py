#!/usr/bin/env python3
"""
Test script for AI Gateway Epic E1 implementation.

This script tests the core AI Gateway functionality including:
- Provider initialization
- Task execution
- Error handling
- Circuit breaker functionality
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.services.ai_client import AIClient
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_provider import TaskType
from app.core.config import settings


async def test_ai_gateway():
    """Test AI Gateway functionality."""
    print("🧪 Testing AI Gateway Epic E1 Implementation")
    print("=" * 50)
    
    # Test 1: Configuration
    print("\n1. Testing Configuration Integration")
    print("-" * 30)
    print(f"AI Gateway Enabled: {getattr(settings, 'ai_gateway_enabled', False)}")
    print(f"AI Gateway Experimental: {getattr(settings, 'ai_gateway_experimental', False)}")
    print(f"Primary Provider: {getattr(settings, 'ai_gateway_primary_provider', 'openai')}")
    print(f"Fallback Providers: {getattr(settings, 'ai_gateway_fallback_providers_list', [])}")
    
    # Test 2: AI Client Initialization
    print("\n2. Testing AI Client Initialization")
    print("-" * 30)
    try:
        ai_client = AIClient()
        print(f"✅ AI Client initialized successfully")
        print(f"Providers: {list(ai_client.providers.keys())}")
        print(f"Primary Provider: {ai_client.primary_provider}")
        print(f"Fallback Providers: {ai_client.fallback_providers}")
    except Exception as e:
        print(f"❌ AI Client initialization failed: {e}")
        return False
    
    # Test 3: Provider Status
    print("\n3. Testing Provider Status")
    print("-" * 30)
    status = ai_client.get_provider_status()
    for provider_name, provider_status in status.items():
        print(f"Provider: {provider_name}")
        print(f"  Available: {provider_status['available']}")
        print(f"  Healthy: {provider_status['healthy']}")
        print(f"  Status: {provider_status['status']}")
        print(f"  Capabilities: {provider_status['capabilities']}")
        print(f"  Circuit Breaker: {provider_status['circuit_breaker']['state']}")
    
    # Test 4: AI Orchestrator
    print("\n4. Testing AI Orchestrator")
    print("-" * 30)
    try:
        orchestrator = AIOrchestrator()
        orchestrator.initialize()
        print(f"✅ AI Orchestrator initialized successfully")
        
        # Test status
        ai_status = orchestrator.get_ai_status()
        print(f"AI Gateway Enabled: {ai_status['enabled']}")
        print(f"Experimental Mode: {ai_status['experimental']}")
        print(f"Available Providers: {len(ai_status['providers'])}")
    except Exception as e:
        print(f"❌ AI Orchestrator initialization failed: {e}")
        return False
    
    # Test 5: Task Execution (Query Analysis)
    print("\n5. Testing Task Execution")
    print("-" * 30)
    try:
        test_query = "لنت ترمز چری تیگو 8"
        print(f"Testing query analysis for: '{test_query}'")
        
        analysis = await orchestrator.analyze_query(test_query)
        print(f"✅ Query analysis completed")
        print(f"Analysis result: {analysis}")
        
    except Exception as e:
        print(f"❌ Task execution failed: {e}")
        return False
    
    # Test 6: Intelligent Search
    print("\n6. Testing Intelligent Search")
    print("-" * 30)
    try:
        test_parts = [
            {
                "part_name": "Brake Pad",
                "brand_oem": "Chery",
                "vehicle_make": "Chery",
                "vehicle_model": "Tiggo 8",
                "category": "Brake System"
            },
            {
                "part_name": "Oil Filter",
                "brand_oem": "Chery",
                "vehicle_make": "Chery",
                "vehicle_model": "Tiggo 8",
                "category": "Engine"
            }
        ]
        
        intelligent_result = await orchestrator.intelligent_search(test_query, test_parts)
        print(f"✅ Intelligent search completed")
        print(f"Success: {intelligent_result.get('success', False)}")
        print(f"Search Type: {intelligent_result.get('search_type', 'unknown')}")
        if intelligent_result.get('query_analysis'):
            print(f"Query Analysis: {intelligent_result['query_analysis']}")
        if intelligent_result.get('suggestions'):
            print(f"Suggestions: {intelligent_result['suggestions']}")
            
    except Exception as e:
        print(f"❌ Intelligent search failed: {e}")
        return False
    
    # Test 7: Semantic Search
    print("\n7. Testing Semantic Search")
    print("-" * 30)
    try:
        semantic_results = await orchestrator.semantic_search(test_query, test_parts)
        print(f"✅ Semantic search completed")
        print(f"Results count: {len(semantic_results)}")
        if semantic_results:
            print(f"Top result: {semantic_results[0]}")
            
    except Exception as e:
        print(f"❌ Semantic search failed: {e}")
        return False
    
    print("\n🎉 All AI Gateway tests completed successfully!")
    return True


async def main():
    """Main test function."""
    try:
        success = await test_ai_gateway()
        if success:
            print("\n✅ Epic E1 implementation is working correctly!")
            return 0
        else:
            print("\n❌ Epic E1 implementation has issues!")
            return 1
    except Exception as e:
        print(f"\n💥 Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
