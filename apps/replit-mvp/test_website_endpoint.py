#!/usr/bin/env python3
"""
Test the website creation endpoint directly
"""

import asyncio
import httpx
import json

async def test_website_creation():
    print("🌐 Testing Website Creation Endpoint")
    print("=" * 50)
    
    # Test data
    test_data = {
        "business_name": "Aiden SuperIntelligence",
        "industry": "ai_automation",
        "type": "landing_page",
        "style": "modern", 
        "features": ["contact_form", "testimonials"],
        "include_blog": False,
        "domain": "aidensuperai.com",
        "account_id": "test_user"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print("📡 Sending request to /api/create-website...")
            print(f"📋 Data: {json.dumps(test_data, indent=2)}")
            
            response = await client.post(
                "http://localhost:8001/api/create-website",
                headers={"Content-Type": "application/json"},
                json=test_data
            )
            
            print(f"📊 Status Code: {response.status_code}")
            print(f"📄 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['success']}")
                if result['success']:
                    print(f"🌟 Result: {result['result'][:300]}...")
                else:
                    print(f"❌ Error: {result}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Request Error: {e}")
        import traceback
        print(f"🔍 Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_website_creation())