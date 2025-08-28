#!/usr/bin/env python3
"""
Test Real Client Scenario: Dwyer Heating and Air
=================================================

Test exactly what the user described:
- HVAC client "Dwyer Heating and Air"  
- They miss a lot of calls
- Aiden should automatically set up SMS system, n8n, Twilio, etc.
- Should create client files and track everything
"""

import asyncio
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def test_real_client_scenario():
    """Test Aiden handling a real client automation request"""
    
    print("🏢 REAL CLIENT SCENARIO TEST")
    print("=" * 60)
    print("📋 Scenario: HVAC client 'Dwyer Heating and Air' misses a lot of calls")
    print("🎯 Expected: Aiden should proactively set up complete SMS automation")
    print("=" * 60)
    
    # Initialize the client's business
    print("\n🚀 Initializing client: Dwyer Heating and Air...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="Dwyer Heating and Air",
        industry="hvac",
        context={
            "client_type": "HVAC contractor",
            "main_issue": "missing too many calls",
            "service_area": "Local metro area",
            "business_hours": "8 AM - 6 PM Mon-Fri",
            "emergency_services": True,
            "avg_ticket_value": 350
        }
    )
    
    business_key = "dwyer_heating_and_air_hvac"
    print(f"✅ Client business initialized: {assistant_id}")
    
    # The exact scenario the user described
    print("\n" + "="*60)
    print("💬 USER REQUEST TO AIDEN:")
    print("\"I need a solution for a HVAC client who has a company called")
    print("Dwyer Heating and air, they miss a lot of calls.\"")
    print("="*60)
    
    try:
        response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="I need a solution for a HVAC client who has a company called Dwyer Heating and air, they miss a lot of calls.",
            context={
                "client_request": True,
                "automation_needed": "missed_call_management", 
                "urgency": "high",
                "setup_required": ["sms", "n8n", "twilio", "email", "deployment"]
            }
        )
        
        print(f"\n🤖 AIDEN'S COMPLETE RESPONSE:")
        print("-" * 60)
        print(response)
        print("-" * 60)
        
        print("\n✅ SCENARIO TEST COMPLETED!")
        
        # Test follow-up request
        print("\n" + "="*60) 
        print("💬 FOLLOW-UP REQUEST:")
        print("\"Also create them a website with an AI agent that can answer")
        print("questions about their HVAC business\"")
        print("="*60)
        
        followup_response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
            business_key=business_key,
            message="Also create them a website with an AI agent that can answer questions about their HVAC business",
            context={
                "website_needed": True,
                "ai_agent_required": True,
                "business_qa": True
            }
        )
        
        print(f"\n🤖 AIDEN'S WEBSITE + AI AGENT RESPONSE:")
        print("-" * 60)
        print(followup_response)
        print("-" * 60)
        
        print("\n🎉 COMPLETE CLIENT AUTOMATION TEST FINISHED!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_real_client_scenario())