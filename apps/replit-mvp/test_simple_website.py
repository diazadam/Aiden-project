#!/usr/bin/env python3
"""
Test website creation with a simpler request
"""

import asyncio
import httpx
import json

async def test_simple_website():
    print("🌐 Testing Simple Website Creation")
    print("=" * 50)
    
    # Very simple test data
    test_data = {
        "business_name": "Test Business",
        "industry": "general",
        "type": "landing_page",
        "style": "modern",
        "features": ["contact_form"],
        "include_blog": False,
        "account_id": "test"
    }
    
    try:
        # Use a longer timeout
        async with httpx.AsyncClient(timeout=120.0) as client:
            print("📡 Sending simple request...")
            print(f"📋 Data: {json.dumps(test_data, indent=2)}")
            
            response = await client.post(
                "http://localhost:8001/api/create-website",
                headers={"Content-Type": "application/json"},
                json=test_data
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result['success']}")
                if result['success']:
                    print(f"🌟 Website Created!")
                    print(f"📄 First 300 chars: {result['result'][:300]}...")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"📄 Response: {response.text}")
                
    except httpx.ReadTimeout:
        print("⏰ Request timed out - the website creation is taking too long")
        print("This suggests the OpenAI API call is working but slow")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_simple_website())