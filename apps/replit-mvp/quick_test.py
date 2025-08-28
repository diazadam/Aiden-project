#!/usr/bin/env python3
"""
Quick test to verify all systems are working before the full demo
"""

import asyncio
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def quick_test():
    print("🔍 Quick System Test")
    print("=" * 40)
    
    try:
        # Test 1: Basic initialization
        print("1. Testing business initialization...")
        assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
            business_name="Test Business",
            industry="test",
            context={"test": True}
        )
        print(f"✅ Assistant created: {assistant_id}")
        
        # Test 2: Basic conversation
        print("\n2. Testing conversation...")
        response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key="test_business_test",
            message="Hello! Can you help me automate my business?",
            context={"test_mode": True}
        )
        print(f"✅ Conversation works: {response[:100]}...")
        
        # Test 3: Learning pattern
        print("\n3. Testing learning capability...")
        learn_result = await AIDEN_SUPERINTELLIGENCE.learn_new_automation_pattern(
            business_key="test_business_test",
            pattern_description="Test pattern: Send welcome messages to new customers",
            examples=[{"trigger": "New customer signup", "action": "Send welcome email"}]
        )
        print(f"✅ Learning works: {learn_result[:100]}...")
        
        print("\n🎉 All systems operational! Ready for full demo.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(quick_test())