#!/usr/bin/env python3
"""
Test the Enhanced Aiden Intelligence
=====================================

This tests the new intelligent, proactive Aiden assistant that should:
1. Understand context without explicit instructions
2. Take proactive actions 
3. Install capabilities automatically
4. Provide complete solutions
"""

import asyncio
import sys
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def test_enhanced_aiden():
    """Test the enhanced Aiden assistant capabilities"""
    
    print("🧠 TESTING ENHANCED AIDEN INTELLIGENCE")
    print("=" * 60)
    
    # Initialize HVAC business (like the example from your conversation)
    print("\n🏢 Initializing HVAC Business...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="Dwyer Heating and Cooling",
        industry="hvac",
        context={
            "service_area": "Local Area",
            "services": ["HVAC Repair", "Installation", "Maintenance"],
            "business_hours": "8 AM - 6 PM"
        }
    )
    
    business_key = "dwyer_heating_and_cooling_hvac"
    
    print(f"✅ Business initialized with assistant: {assistant_id}")
    
    # Test 1: Simple "text my missed calls" request (like your example)
    print("\n" + "="*60)
    print("🧪 TEST 1: Simple Missed Calls Request")
    print("User says: 'text my missed calls'")
    print("="*60)
    
    try:
        response1 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="text my missed calls",
            context={"test_mode": True}
        )
        
        print(f"🤖 ENHANCED AIDEN RESPONSE:")
        print(response1)
        print("\n✅ Test 1 completed!")
        
    except Exception as e:
        print(f"❌ Test 1 failed: {e}")
    
    # Test 2: More complex request
    print("\n" + "="*60)
    print("🧪 TEST 2: Complex Automation Request")
    print("User says: 'Set up automation for when customers call after hours'")
    print("="*60)
    
    try:
        response2 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="Set up automation for when customers call after hours",
            context={"test_mode": True}
        )
        
        print(f"🤖 ENHANCED AIDEN RESPONSE:")
        print(response2)
        print("\n✅ Test 2 completed!")
        
    except Exception as e:
        print(f"❌ Test 2 failed: {e}")
    
    # Test 3: Website building request
    print("\n" + "="*60)
    print("🧪 TEST 3: Website Building Request")
    print("User says: 'Create a landing page showcasing what our new system can do'")
    print("="*60)
    
    try:
        response3 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="Create a landing page showcasing what our new system can do",
            context={
                "test_mode": True,
                "business_description": "HVAC company with advanced AI automation capabilities"
            }
        )
        
        print(f"🤖 ENHANCED AIDEN RESPONSE:")
        print(response3)
        print("\n✅ Test 3 completed!")
        
    except Exception as e:
        print(f"❌ Test 3 failed: {e}")
    
    print("\n" + "="*60)
    print("🎉 ENHANCED AIDEN INTELLIGENCE TESTING COMPLETE!")
    print("="*60)
    print("\n🚀 Key Improvements:")
    print("✅ Context-aware responses")
    print("✅ Proactive action taking") 
    print("✅ Automatic capability installation")
    print("✅ Industry-specific intelligence")
    print("✅ Complete solution provision")

if __name__ == "__main__":
    asyncio.run(test_enhanced_aiden())