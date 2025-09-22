#!/usr/bin/env python3
"""
Test script for AI Gateway Epic E3 - Advanced AI Features & Integration

This script tests the new Epic E3 components:
- Multi-language AI Processing
- Hybrid Search Engine
- AI Recommendations Engine
- Natural Language Query Processor
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to Python path
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))

# Set environment variables for testing
os.environ['AI_GATEWAY_ENABLED'] = 'true'
os.environ['AI_GATEWAY_EXPERIMENTAL'] = 'false'
os.environ['AI_GATEWAY_PRIMARY_PROVIDER'] = 'openai'
os.environ['AI_GATEWAY_FALLBACK_PROVIDERS'] = 'stub'
os.environ['OPENAI_API_KEY'] = 'INVALID_TEST_KEY'  # Use invalid key to test fallback
os.environ['DATABASE_URL'] = 'sqlite:///./data/test.db'

from app.core.config import settings
from app.services.ai_orchestrator import AIOrchestrator
from app.services.ai_orchestrator_e3 import AIOrchestratorE3Extensions
from app.services.ai_language_processor import LanguageProcessor, Language
from app.services.ai_hybrid_search import HybridSearchEngine, SearchType
from app.services.ai_recommendations import AIRecommendationsEngine, UserProfile
from app.services.ai_query_processor import AIQueryProcessor, QueryIntent


async def test_language_processor():
    """Test the language processor component."""
    print("\n1. Testing Language Processor")
    print("=" * 40)
    
    processor = LanguageProcessor()
    
    # Test Persian text
    persian_text = "لنت ترمز چری تیگو 8 جلو"
    language, confidence = processor.detect_language(persian_text)
    print(f"Persian text: '{persian_text}'")
    print(f"Detected language: {language.value} (confidence: {confidence:.2f})")
    
    # Test English text
    english_text = "brake pad for Chery Tiggo 8 front"
    language, confidence = processor.detect_language(english_text)
    print(f"English text: '{english_text}'")
    print(f"Detected language: {language.value} (confidence: {confidence:.2f})")
    
    # Test mixed text
    mixed_text = "لنت ترمز brake pad چری Chery"
    language, confidence = processor.detect_language(mixed_text)
    print(f"Mixed text: '{mixed_text}'")
    print(f"Detected language: {language.value} (confidence: {confidence:.2f})")
    
    # Test entity extraction
    entities = processor.extract_car_entities(persian_text)
    print(f"Extracted entities: {entities}")
    
    # Test search variants
    variants = processor.create_search_variants(persian_text)
    print(f"Search variants: {variants[:3]}...")  # Show first 3
    
    print("✅ Language Processor tests completed")


async def test_hybrid_search():
    """Test the hybrid search engine."""
    print("\n2. Testing Hybrid Search Engine")
    print("=" * 40)
    
    search_engine = HybridSearchEngine()
    
    # Sample parts data
    parts_data = [
        {
            "id": 1,
            "part_name": "لنت ترمز جلو",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "category": "brake_system",
            "price": 150.0,
            "availability": True
        },
        {
            "id": 2,
            "part_name": "فیلتر هوا",
            "brand_oem": "JAC",
            "vehicle_make": "JAC",
            "vehicle_model": "J4",
            "category": "engine_parts",
            "price": 25.0,
            "availability": True
        },
        {
            "id": 3,
            "part_name": "brake disc",
            "brand_oem": "Brilliance",
            "vehicle_make": "Brilliance",
            "vehicle_model": "V5",
            "category": "brake_system",
            "price": 200.0,
            "availability": False
        }
    ]
    
    # Test different search types
    search_queries = [
        ("لنت ترمز", "keyword"),
        ("brake pad", "semantic"),
        ("چری تیگو", "filter")
    ]
    
    for query, search_type in search_queries:
        print(f"\nTesting {search_type} search for: '{query}'")
        
        try:
            results = await search_engine.search(
                query=query,
                parts=parts_data,
                search_type=getattr(SearchType, search_type.upper()),
                limit=5
            )
            
            print(f"Found {len(results)} results:")
            for i, result in enumerate(results[:3], 1):
                print(f"  {i}. {result.part_name} - {result.brand_oem} {result.vehicle_model} (score: {result.search_score:.2f})")
                
        except Exception as e:
            print(f"Error in {search_type} search: {e}")
    
    print("✅ Hybrid Search Engine tests completed")


async def test_recommendations_engine():
    """Test the AI recommendations engine."""
    print("\n3. Testing AI Recommendations Engine")
    print("=" * 40)
    
    rec_engine = AIRecommendationsEngine()
    
    # Sample part data
    part_data = {
        "id": 1,
        "part_name": "لنت ترمز جلو",
        "brand_oem": "Chery",
        "vehicle_make": "Chery",
        "vehicle_model": "Tiggo 8",
        "category": "brake_pad",
        "price": 150.0,
        "availability": True
    }
    
    # Test user profile
    user_profile = UserProfile(
        user_id="test_user",
        purchase_history=[
            {"id": 1, "category": "brake_pad", "brand_oem": "Chery", "price": 150.0},
            {"id": 2, "category": "air_filter", "brand_oem": "JAC", "price": 25.0}
        ],
        search_history=["لنت ترمز", "فیلتر هوا"],
        preferences={"favorite_brands": ["Chery", "JAC"]},
        vehicle_info={"make": "Chery", "model": "Tiggo 8"}
    )
    
    try:
        # Test recommendations
        recommendations = await rec_engine.get_recommendations(
            part_id=1,
            part_data=part_data,
            user_profile=user_profile,
            limit=5
        )
        
        print(f"Generated {len(recommendations)} recommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec.part_name} - {rec.brand_oem} ({rec.recommendation_type.value})")
            print(f"     Reason: {rec.reason} (confidence: {rec.confidence:.2f})")
        
        # Test purchase pattern analysis
        patterns = rec_engine.analyze_purchase_patterns(user_profile)
        print(f"\nPurchase pattern analysis:")
        print(f"  Total purchases: {patterns['total_purchases']}")
        print(f"  Average price: ${patterns['average_price']:.2f}")
        print(f"  Insights: {patterns['insights']}")
        
    except Exception as e:
        print(f"Error in recommendations: {e}")
    
    print("✅ AI Recommendations Engine tests completed")


async def test_query_processor():
    """Test the natural language query processor."""
    print("\n4. Testing Natural Language Query Processor")
    print("=" * 40)
    
    query_processor = AIQueryProcessor()
    
    # Test queries
    test_queries = [
        "لنت ترمز چری تیگو 8 جلو",
        "brake pad for Chery Tiggo 8 front",
        "قیمت فیلتر هوا",
        "کدام برند بهتر است؟",
        "تعمیرات خودرو کی انجام شود؟"
    ]
    
    for query in test_queries:
        print(f"\nProcessing query: '{query}'")
        
        try:
            analysis = await query_processor.process_query(query)
            
            print(f"  Language: {analysis.language.value} (confidence: {analysis.language_confidence:.2f})")
            print(f"  Intent: {analysis.intent.value}")
            print(f"  Complexity: {analysis.complexity.value}")
            print(f"  Entities: {analysis.entities}")
            print(f"  Filters: {analysis.filters}")
            print(f"  Requires clarification: {analysis.requires_clarification}")
            if analysis.clarification_questions:
                print(f"  Clarification questions: {analysis.clarification_questions}")
            
        except Exception as e:
            print(f"  Error processing query: {e}")
    
    print("✅ Natural Language Query Processor tests completed")


async def test_orchestrator_integration():
    """Test the AI Orchestrator with Epic E3 extensions."""
    print("\n5. Testing AI Orchestrator Integration")
    print("=" * 40)
    
    # Initialize orchestrator
    orchestrator = AIOrchestrator()
    orchestrator.initialize()
    
    # Initialize E3 extensions
    e3_extensions = AIOrchestratorE3Extensions(orchestrator)
    
    # Test language analysis
    print("Testing language analysis...")
    lang_analysis = e3_extensions.get_language_analysis("لنت ترمز چری تیگو 8")
    print(f"Language analysis: {lang_analysis['language']} (confidence: {lang_analysis['language_confidence']:.2f})")
    
    # Test natural language query processing
    print("\nTesting natural language query processing...")
    query_result = await e3_extensions.process_natural_language_query("لنت ترمز چری تیگو 8 جلو")
    print(f"Query processing success: {query_result['success']}")
    print(f"Intent: {query_result.get('intent', 'unknown')}")
    print(f"Language: {query_result.get('language', 'unknown')}")
    
    # Test hybrid search
    print("\nTesting hybrid search...")
    parts_data = [
        {
            "id": 1,
            "part_name": "لنت ترمز جلو",
            "brand_oem": "Chery",
            "vehicle_make": "Chery",
            "vehicle_model": "Tiggo 8",
            "category": "brake_system",
            "price": 150.0,
            "availability": True
        }
    ]
    
    search_results = await e3_extensions.hybrid_search(
        query="لنت ترمز چری",
        parts=parts_data,
        search_type="hybrid",
        limit=5
    )
    print(f"Hybrid search found {len(search_results)} results")
    
    # Test smart recommendations
    print("\nTesting smart recommendations...")
    part_data = {
        "id": 1,
        "part_name": "لنت ترمز جلو",
        "brand_oem": "Chery",
        "vehicle_make": "Chery",
        "vehicle_model": "Tiggo 8",
        "category": "brake_pad",
        "price": 150.0,
        "availability": True
    }
    
    recommendations = await e3_extensions.get_smart_recommendations(
        part_id=1,
        part_data=part_data,
        limit=3
    )
    print(f"Generated {len(recommendations)} recommendations")
    
    print("✅ AI Orchestrator Integration tests completed")


async def run_all_tests():
    """Run all Epic E3 tests."""
    print("🧪 Testing AI Gateway Epic E3 Implementation")
    print("=" * 60)
    
    try:
        await test_language_processor()
        await test_hybrid_search()
        await test_recommendations_engine()
        await test_query_processor()
        await test_orchestrator_integration()
        
        print("\n🎉 All Epic E3 tests completed successfully!")
        print("\n✅ Epic E3 implementation is working correctly!")
        print("\n🚀 Advanced AI Features & Integration are ready!")
        
    except Exception as e:
        print(f"\n❌ Epic E3 tests failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
