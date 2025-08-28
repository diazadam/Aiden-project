#!/usr/bin/env python3
"""
Test Real Aiden with Full System Control
========================================

This tests the REAL Aiden assistant with actual system control capabilities.
"""

import asyncio
import os
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def test_real_aiden_system_control():
    """Test Aiden with real system control"""
    
    print("🚀 TESTING REAL AIDEN WITH FULL SYSTEM CONTROL")
    print("=" * 70)
    print("⚠️  WARNING: This will actually control your Mac!")
    print("✨ Aiden will open browsers, send SMS, deploy websites")
    print("=" * 70)
    
    # Initialize client with real assistant
    print("\n🏢 Initializing client with REAL Aiden assistant...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="Dwyer Heating and Air",
        industry="hvac",
        context={
            "main_issue": "missing too many calls - need REAL automation",
            "phone": "+15551234567",
            "website_needed": True,
            "sms_automation_required": True
        }
    )
    
    business_key = "dwyer_heating_and_air_hvac"
    print(f"✅ Real assistant initialized: {assistant_id}")
    
    # The REAL test - this will actually execute
    print("\n" + "="*70)
    print("🎯 REAL TEST: Complete Client Automation Setup")
    print("User request: 'Set up everything for Dwyer Heating and Air - they miss calls'")
    print("="*70)
    print("🔥 Aiden will now ACTUALLY:")
    print("  • Control your Mac and open browser tabs")
    print("  • Set up real Twilio SMS account")
    print("  • Deploy actual website with AI agent")
    print("  • Send real SMS messages")
    print("  • Execute system commands")
    print("="*70)
    
    # Auto-proceed for testing
    print("\n✅ AUTO-PROCEEDING WITH REAL SYSTEM CONTROL TEST")
    
    print("\n🚀 EXECUTING REAL AUTOMATION...")
    
    try:
        # This will call the REAL assistant with REAL system control
        real_response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="I need a complete automation solution for my HVAC client Dwyer Heating and Air. They miss a lot of calls and need real SMS automation, a website with AI agent, and full system setup. Execute everything now with real system control.",
            context={
                "execute_real_automation": True,
                "system_control_approved": True,
                "twilio_setup_required": True,
                "website_deployment_required": True,
                "client_phone": "+15551234567",
                "urgency": "high"
            }
        )
        
        print("\n🤖 REAL AIDEN'S RESPONSE:")
        print("-" * 60)
        print(real_response)
        print("-" * 60)
        
        print("\n✅ REAL AUTOMATION TEST COMPLETED!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🔥 REAL AIDEN SYSTEM CONTROL TEST")
    print("This will test actual Mac automation, browser control, SMS sending, etc.")
    asyncio.run(test_real_aiden_system_control())