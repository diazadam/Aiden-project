#!/usr/bin/env python3
"""
Debug the website creation functionality directly
"""

import asyncio
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def debug_website_creation():
    print("🔍 Debugging Website Creation")
    print("=" * 50)
    
    try:
        # Step 1: Initialize business
        print("1. Initializing business...")
        assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
            business_name="Test Website Business",
            industry="technology",
            context={"test": True}
        )
        print(f"✅ Assistant created: {assistant_id}")
        
        # Step 2: Try creating website
        print("\n2. Creating website...")
        website_spec = {
            "type": "landing_page",
            "style": "modern", 
            "features": ["contact_form"],
            "include_blog": False,
            "domain": "testysite.com"
        }
        
        website_result = await AIDEN_SUPERINTELLIGENCE.create_website(
            business_key="test_website_business_technology",
            website_spec=website_spec
        )
        
        print(f"✅ Website created: {website_result[:200]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        print(f"🔍 Full traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(debug_website_creation())