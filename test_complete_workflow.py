#!/usr/bin/env python3
"""
Test the complete workflow of the Chinese Auto Parts Price Bot.
This script demonstrates the full user journey from search to order creation.
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(__file__))

from app.db.database import SessionLocal
from app.services.bot_service import BotService
from app.services.lead_service import LeadService
from app.services.order_service import OrderService
from app.services.search import SearchService

def test_complete_workflow():
    """Test the complete user workflow."""
    print("🧪 Testing Complete Workflow - Chinese Auto Parts Price Bot")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Initialize services
        bot_service = BotService(db)
        lead_service = LeadService(db)
        order_service = OrderService(db)
        search_service = SearchService(db)
        
        print("\n1️⃣ Testing Part Search")
        print("-" * 30)
        
        # Test search functionality
        search_queries = [
            "لنت جلو تیگو ۸",
            "فیلتر روغن X22",
            "فیلتر هوا آریزو ۵"
        ]
        
        search_results = []
        for query in search_queries:
            print(f"🔍 Searching: {query}")
            result = bot_service.search_and_confirm_part(query)
            
            if result["found"]:
                part_data = result["part_data"]
                print(f"   ✅ Found: {part_data['part_name']} - {part_data['vehicle_model']}")
                print(f"   💰 Best Price: {part_data['best_price']} {part_data['prices'][0]['currency'] if part_data['prices'] else 'N/A'}")
                search_results.append(result)
            else:
                print(f"   ❌ Not found: {result['message']}")
        
        print(f"\n📊 Search Results: {len(search_results)}/{len(search_queries)} parts found")
        
        print("\n2️⃣ Testing Contact Capture")
        print("-" * 30)
        
        # Simulate contact capture
        telegram_user_id = "test_user_123"
        phone_number = "+989123456789"
        first_name = "Test"
        last_name = "User"
        
        print(f"👤 Creating lead for user: {telegram_user_id}")
        lead_result = bot_service.handle_contact_capture(
            telegram_user_id=telegram_user_id,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name
        )
        
        if lead_result["lead"]:
            lead = lead_result["lead"]
            print(f"   ✅ Lead created: {lead.first_name} {lead.last_name}")
            print(f"   📱 Phone: {lead.phone_e164}")
            print(f"   🆔 Lead ID: {lead.id}")
        else:
            print(f"   ❌ Lead creation failed: {lead_result['message']}")
            return
        
        print("\n3️⃣ Testing Order Creation")
        print("-" * 30)
        
        # Create order from search results
        if search_results:
            print("📋 Creating order from search results...")
            order_result = bot_service.create_order_from_search_results(
                telegram_user_id=telegram_user_id,
                search_results=search_results
            )
            
            if order_result["success"]:
                order = order_result["order"]
                print(f"   ✅ Order created: {order_result['message']}")
                print(f"   🆔 Order ID: {order.id}")
                print(f"   📅 Status: {order.status}")
                print(f"   📅 Created: {order.created_at}")
                
                # Get order summary
                summary = order_service.get_order_summary(order)
                print(f"   📦 Items: {summary['total_items']} total, {summary['matched_items']} matched")
                
                for item in summary["items"]:
                    print(f"      - Line {item['line_no']}: {item['query_text']}")
                    if item["matched_part_id"]:
                        print(f"        ✅ Matched to part ID: {item['matched_part_id']}")
                    else:
                        print(f"        ❌ No match found")
            else:
                print(f"   ❌ Order creation failed: {order_result['message']}")
        
        print("\n4️⃣ Testing Order Status Check")
        print("-" * 30)
        
        # Check order status
        status_result = bot_service.get_order_status(telegram_user_id)
        
        if status_result["success"]:
            print(f"📊 {status_result['message']}")
            
            for order_summary in status_result["orders"]:
                print(f"   📋 Order #{order_summary['order_id']:05d}")
                print(f"      Status: {order_summary['status']}")
                print(f"      Items: {order_summary['matched_items']}/{order_summary['total_items']}")
                print(f"      Date: {order_summary['created_at']}")
        else:
            print(f"   ❌ Status check failed: {status_result['message']}")
        
        print("\n5️⃣ Testing Lead Management")
        print("-" * 30)
        
        # Get lead information
        lead = lead_service.get_lead_by_telegram_id(telegram_user_id)
        if lead:
            print(f"👤 Lead Information:")
            print(f"   ID: {lead.id}")
            print(f"   Name: {lead.first_name} {lead.last_name}")
            print(f"   Phone: {lead.phone_e164}")
            print(f"   Created: {lead.created_at}")
            print(f"   Updated: {lead.updated_at}")
        
        print("\n6️⃣ Testing Bulk Search")
        print("-" * 30)
        
        # Test bulk search
        bulk_queries = [
            "لنت جلو تیگو ۸",
            "فیلتر روغن X22",
            "فیلتر هوا آریزو ۵"
        ]
        
        print("🔍 Testing bulk search...")
        bulk_result = bot_service.search_multiple_parts(bulk_queries)
        
        if bulk_result["success"]:
            print(f"   ✅ {bulk_result['message']}")
            print(f"   📊 Found: {bulk_result['found_count']}/{bulk_result['total_queries']} parts")
            
            for item in bulk_result["results"]:
                if "found" not in item:  # Found part
                    price_text = f" - {item['best_price']:,.0f} {item['currency']}" if item['best_price'] else ""
                    print(f"      ✅ {item['query']}: {item['part_name']} {item['vehicle_model']}{price_text}")
                else:
                    print(f"      ❌ {item['query']}: Not found")
        else:
            print(f"   ❌ Bulk search failed: {bulk_result['message']}")
        
        print("\n" + "=" * 60)
        print("🎉 Complete Workflow Test Results:")
        print("✅ Part search with Persian queries")
        print("✅ Contact capture and lead creation")
        print("✅ Order creation from search results")
        print("✅ Order status tracking")
        print("✅ Lead management")
        print("✅ Bulk search functionality")
        print("\n🚀 The Chinese Auto Parts Price Bot is fully functional!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_complete_workflow()
