#!/usr/bin/env python3
"""
Quick test of the new Aiden advanced capabilities.
This verifies that all the new features are working correctly.
"""

import asyncio
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def test_new_capabilities():
    """Test the new advanced capabilities."""
    print("🧪 Testing New Aiden Capabilities...")
    
    try:
        # Test 1: Initialize a business
        print("\n1️⃣ Testing business initialization...")
        await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
            business_name="Test Business",
            industry="restaurant",
            context={"test": True}
        )
        print("✅ Business initialization successful")
        
        # Test 2: Check if new fields are present
        print("\n2️⃣ Testing new data structures...")
        business_key = "test_business_restaurant"
        
        if business_key in AIDEN_SUPERINTELLIGENCE.active_assistants:
            assistant = AIDEN_SUPERINTELLIGENCE.active_assistants[business_key]
            
            # Check for new fields
            required_fields = ['learned_patterns', 'custom_solutions', 'client_preferences']
            for field in required_fields:
                if field in assistant:
                    print(f"✅ {field} field present")
                else:
                    print(f"❌ {field} field missing")
        else:
            print("❌ Business not found in active_assistants")
        
        # Test 3: Test learning new pattern
        print("\n3️⃣ Testing pattern learning...")
        try:
            result = await AIDEN_SUPERINTELLIGENCE.learn_new_automation_pattern(
                business_key=business_key,
                pattern_description="Test automation pattern",
                examples=[{"trigger": "test", "action": "test", "outcome": "test"}]
            )
            print("✅ Pattern learning successful")
        except Exception as e:
            print(f"❌ Pattern learning failed: {e}")
        
        # Test 4: Test custom solution creation
        print("\n4️⃣ Testing custom solution creation...")
        try:
            result = await AIDEN_SUPERINTELLIGENCE.create_custom_automation_solution(
                business_key=business_key,
                client_need="Test client need",
                context={"test": True}
            )
            print("✅ Custom solution creation successful")
        except Exception as e:
            print(f"❌ Custom solution creation failed: {e}")
        
        # Test 5: Test website creation
        print("\n5️⃣ Testing website creation...")
        try:
            result = await AIDEN_SUPERINTELLIGENCE.create_website(
                business_key=business_key,
                website_spec={
                    "type": "landing_page",
                    "style": "modern",
                    "features": ["contact_form"],
                    "include_blog": False
                }
            )
            print("✅ Website creation successful")
        except Exception as e:
            print(f"❌ Website creation failed: {e}")
        
        print("\n🎉 All capability tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_new_capabilities())
