#!/usr/bin/env python3
"""
AIDEN SUPERINTELLIGENCE DEMONSTRATION
====================================

This script demonstrates the power of the integrated superintelligence system:

1. Persistent AI assistants for each business type
2. Industry-specific automation expertise  
3. Function calling for direct API integrations
4. Memory persistence across conversations
5. Seamless integration with the Control Tower

Run this demo to see how businesses can now have their own dedicated AI employees!
"""

import asyncio
import json
from superintelligence import AIDEN_SUPERINTELLIGENCE

async def demo_hvac_business():
    """Demo: HVAC business automation with persistent AI assistant"""
    print("\n" + "="*60)
    print("🔧 HVAC BUSINESS AUTOMATION DEMO")  
    print("="*60)
    
    # Initialize HVAC business automation
    print("🚀 Initializing AI automation for ACME HVAC Solutions...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="ACME HVAC Solutions",
        industry="hvac",
        context={
            "service_area": "Chicago Metro",
            "services": ["AC Repair", "Heating Installation", "Maintenance"],
            "peak_season": "Summer",
            "avg_ticket": 250,
            "established": "2018"
        }
    )
    
    print(f"✅ Created AI Assistant: {assistant_id}")
    
    # Conversation 1: Setup appointment confirmations
    print("\n📞 Business Owner: 'I need to set up appointment confirmations for tomorrow's service calls'")
    response1 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
        business_key="acme_hvac_solutions_hvac",
        message="I need to set up appointment confirmations for tomorrow's service calls. We have 3 appointments: John Smith at 9 AM for AC repair (+15551234567), Sarah Johnson at 1 PM for maintenance (+15559876543), and Mike Wilson at 4 PM for heating installation (+15555678901).",
        context={
            "appointments": [
                {"customer": "John Smith", "phone": "+15551234567", "service": "AC Repair", "time": "9:00 AM"},
                {"customer": "Sarah Johnson", "phone": "+15559876543", "service": "Maintenance", "time": "1:00 PM"},  
                {"customer": "Mike Wilson", "phone": "+15555678901", "service": "Heating Installation", "time": "4:00 PM"}
            ],
            "date": "tomorrow"
        }
    )
    
    print(f"🤖 AI Assistant: {response1}\n")
    
    # Conversation 2: Seasonal maintenance campaign
    print("📞 Business Owner: 'Create a winter maintenance campaign for customers who had AC service last summer'")
    response2 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
        business_key="acme_hvac_solutions_hvac", 
        message="Create a winter maintenance campaign targeting customers who had AC service last summer. Focus on heating system check-ups before the cold season hits.",
        context={
            "season": "winter",
            "target": "previous_ac_customers", 
            "campaign_type": "maintenance_upsell"
        }
    )
    
    print(f"🤖 AI Assistant: {response2}\n")
    
    # Conversation 3: Emergency service workflow
    print("📞 Business Owner: 'A customer just called about no heat - what's our emergency protocol?'")
    response3 = await AIDEN_SUPERINTELLIGENCE.business_conversation(
        business_key="acme_hvac_solutions_hvac",
        message="Emergency call just came in - customer at 456 Oak Street has no heat and it's 20 degrees outside. Customer name is Betty Williams, phone +15552468135. What's our emergency service protocol?",
        context={
            "emergency_type": "no_heat",
            "temperature": "20F",
            "customer": {"name": "Betty Williams", "phone": "+15552468135", "address": "456 Oak Street"},
            "priority": "urgent"
        }
    )
    
    print(f"🤖 AI Assistant: {response3}\n")

async def demo_restaurant_business():
    """Demo: Restaurant automation with order management"""
    print("\n" + "="*60)
    print("🍕 RESTAURANT BUSINESS AUTOMATION DEMO")
    print("="*60)
    
    # Initialize restaurant automation
    print("🚀 Initializing AI automation for Tony's Pizzeria...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="Tony's Pizzeria", 
        industry="restaurant",
        context={
            "cuisine_type": "Italian",
            "service_types": ["Dine-in", "Takeout", "Delivery"],
            "hours": "11 AM - 11 PM",
            "avg_order": 25,
            "delivery_radius": "5 miles"
        }
    )
    
    print(f"✅ Created AI Assistant: {assistant_id}")
    
    # Demo conversation: Order confirmation and tracking
    print("\n📞 Manager: 'Set up order confirmations for our Friday night rush'")
    response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
        business_key="tony's_pizzeria_restaurant",
        message="We're expecting a busy Friday night. Set up order confirmations and delivery tracking for tonight's orders. Also prepare our feedback collection system for after delivery.",
        context={
            "day": "Friday",
            "expected_volume": "high", 
            "peak_hours": "6-9 PM",
            "services_needed": ["order_confirmation", "delivery_tracking", "feedback_collection"]
        }
    )
    
    print(f"🤖 AI Assistant: {response}\n")

async def demo_ecommerce_business():
    """Demo: E-commerce automation with abandoned cart recovery"""
    print("\n" + "="*60)
    print("🛒 E-COMMERCE BUSINESS AUTOMATION DEMO")
    print("="*60)
    
    # Initialize e-commerce automation
    print("🚀 Initializing AI automation for StyleHub Boutique...")
    assistant_id = await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
        business_name="StyleHub Boutique",
        industry="ecommerce", 
        context={
            "platform": "Shopify",
            "product_types": ["Fashion", "Accessories", "Beauty"],
            "avg_order": 85,
            "target_demographic": "Women 25-45",
            "monthly_orders": 1200
        }
    )
    
    print(f"✅ Created AI Assistant: {assistant_id}")
    
    # Demo conversation: Abandoned cart recovery
    print("\n📞 Store Owner: 'Our cart abandonment rate is high - set up recovery campaigns'")
    response = await AIDEN_SUPERINTELLIGENCE.business_conversation(
        business_key="stylehub_boutique_ecommerce",
        message="Our cart abandonment rate is 68% which is hurting our revenue. Set up an automated abandoned cart recovery campaign with personalized messages and incentives.",
        context={
            "abandonment_rate": "68%",
            "current_revenue_loss": "$15000/month",
            "campaign_goals": ["recover_sales", "personalize_messaging", "increase_conversion"]
        }
    )
    
    print(f"🤖 AI Assistant: {response}\n")

async def main():
    """Run the complete superintelligence demonstration"""
    print("🧠 AIDEN SUPERINTELLIGENCE SYSTEM DEMONSTRATION")
    print("=" * 80)
    print("Welcome to the future of business automation!")
    print("Each business gets its own dedicated AI employee that:")
    print("• Remembers every conversation and context")
    print("• Understands industry-specific needs") 
    print("• Can directly execute automations via API calls")
    print("• Continuously improves business operations")
    print("=" * 80)
    
    try:
        # Run all business demos
        await demo_hvac_business()
        await demo_restaurant_business() 
        await demo_ecommerce_business()
        
        print("\n" + "="*80)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("="*80)
        print("The Aiden SuperIntelligence system is now fully integrated with the Control Tower.")
        print("Each business type now has specialized AI assistants with:")
        print("✅ Persistent memory across all conversations")
        print("✅ Industry-specific automation expertise") 
        print("✅ Direct API integration capabilities")
        print("✅ Proactive business optimization suggestions")
        print("\nYour Control Tower is ready to build million-dollar automation systems! 🚀")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Demo Error: {e}")
        print("Make sure your OpenAI API key is configured in .env.local")

if __name__ == "__main__":
    asyncio.run(main())