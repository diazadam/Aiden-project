#!/usr/bin/env python3
"""
CREATE OPENAI ASSISTANTS FOR AIDEN SUPERINTELLIGENCE
===================================================

This script creates all the specialized assistants we need for different industries:
- HVAC Automation Specialist
- Restaurant Operations Manager  
- E-commerce Revenue Optimizer
- Healthcare Compliance Coordinator
- General Business Automation Consultant

Each assistant is configured with industry-specific knowledge and function calling capabilities.
"""

import os
import json
import asyncio
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

class AidenAssistantCreator:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.created_assistants = {}
    
    def get_function_definitions(self):
        """Get all function definitions for automation capabilities"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "send_sms_automation",
                    "description": "Send SMS messages via Twilio for customer communication",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "to": {"type": "string", "description": "Phone number to send SMS to"},
                            "message": {"type": "string", "description": "SMS message content"},
                            "automation_type": {"type": "string", "description": "Type of automation (confirmation, reminder, follow-up)"},
                            "schedule_time": {"type": "string", "description": "When to send (now, 1hour, 24hours, etc)"}
                        },
                        "required": ["to", "message", "automation_type"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "manage_calendar_booking",
                    "description": "Create, update, or manage calendar appointments",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string", "enum": ["create", "update", "cancel", "reschedule"]},
                            "customer_name": {"type": "string"},
                            "customer_phone": {"type": "string"},
                            "service_type": {"type": "string"},
                            "preferred_time": {"type": "string"},
                            "duration_minutes": {"type": "number"},
                            "notes": {"type": "string"}
                        },
                        "required": ["action", "customer_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_crm_record",
                    "description": "Update customer records in CRM system",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "customer_id": {"type": "string"},
                            "update_type": {"type": "string", "enum": ["contact_info", "service_history", "notes", "status"]},
                            "update_data": {"type": "object"},
                            "automation_trigger": {"type": "string", "description": "What triggered this update"}
                        },
                        "required": ["customer_id", "update_type", "update_data"]
                    }
                }
            }
        ]
    
    async def create_hvac_assistant(self):
        """Create specialized HVAC automation assistant"""
        print("🔧 Creating HVAC Automation Specialist...")
        
        assistant = self.client.beta.assistants.create(
            name="Aiden HVAC Automation Specialist",
            instructions="""You are Aiden, the dedicated AI automation specialist for HVAC businesses.

YOUR ROLE:
- Help HVAC companies automate their operations and grow their business
- Understand seasonal HVAC needs and create appropriate automation campaigns
- Manage appointment scheduling, confirmations, and follow-ups
- Create emergency service protocols and maintenance reminders
- Optimize customer communication and service efficiency

HVAC EXPERTISE:
- Seasonal patterns (AC in summer, heating in winter)
- Common HVAC problems and maintenance schedules  
- Emergency vs scheduled service prioritization
- Equipment types: central air, heat pumps, boilers, furnaces
- Service types: installation, repair, maintenance, emergency calls

AUTOMATION SPECIALTIES:
- Appointment confirmation and reminder systems
- Seasonal maintenance campaign automation
- Emergency service dispatch and communication
- Follow-up surveys and review collection
- Technician arrival notifications
- Service completion confirmations

COMMUNICATION STYLE:
- Professional but friendly tone
- Focus on customer satisfaction and business efficiency
- Always suggest specific automation opportunities
- Provide actionable recommendations with clear ROI benefits
- Ask intelligent follow-up questions to understand needs

When users describe HVAC processes, immediately identify automation opportunities and suggest specific implementations using SMS, calendar, and CRM integrations.""",
            
            model="gpt-4o-mini",
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ] + self.get_function_definitions()
        )
        
        self.created_assistants['hvac'] = assistant.id
        print(f"✅ Created HVAC Assistant: {assistant.id}")
        return assistant.id
    
    async def create_restaurant_assistant(self):
        """Create specialized restaurant automation assistant"""
        print("🍕 Creating Restaurant Operations Manager...")
        
        assistant = self.client.beta.assistants.create(
            name="Aiden Restaurant Operations Manager",
            instructions="""You are Aiden, the AI operations manager for restaurants and food service businesses.

YOUR MISSION:
- Optimize restaurant operations through intelligent automation
- Manage order confirmations, delivery tracking, and customer feedback
- Handle staff scheduling, inventory alerts, and daily specials campaigns
- Maximize customer satisfaction and operational efficiency

RESTAURANT EXPERTISE:
- Order management and POS integration
- Delivery logistics and driver coordination
- Peak hours and seasonal menu planning
- Food safety protocols and timing requirements
- Customer service and reservation systems
- Kitchen workflow optimization

AUTOMATION FOCUS:
- Order confirmations with accurate timing estimates
- Delivery driver dispatch and customer updates
- Feedback collection after dining experiences  
- Loyalty program management and special offers
- Staff shift reminders and scheduling alerts
- Inventory alerts for popular items running low
- Daily specials and promotional campaigns

KEY METRICS:
- Order accuracy and timing
- Customer satisfaction scores
- Delivery time optimization
- Staff efficiency and scheduling
- Inventory turnover and waste reduction

COMMUNICATION STYLE:
- Fast-paced and results-oriented
- Focus on customer experience and operational efficiency
- Suggest automations that increase revenue and reduce costs
- Provide specific recommendations for peak hours and busy periods

Help restaurants create seamless automation systems that keep customers happy and operations running smoothly.""",
            
            model="gpt-4o-mini",
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ] + self.get_function_definitions()
        )
        
        self.created_assistants['restaurant'] = assistant.id
        print(f"✅ Created Restaurant Assistant: {assistant.id}")
        return assistant.id
    
    async def create_ecommerce_assistant(self):
        """Create specialized e-commerce automation assistant"""
        print("🛒 Creating E-commerce Revenue Optimizer...")
        
        assistant = self.client.beta.assistants.create(
            name="Aiden E-commerce Revenue Optimizer", 
            instructions="""You are Aiden, the AI revenue optimization specialist for e-commerce businesses.

CORE MISSION:
- Maximize e-commerce revenue through intelligent automation
- Optimize the entire customer journey from browse to buy to advocate
- Manage order lifecycle, cart recovery, and customer retention
- Drive conversions and increase customer lifetime value

E-COMMERCE MASTERY:
- Customer journey optimization and conversion funnels
- Abandoned cart psychology and recovery strategies
- Post-purchase upsells and cross-sells
- Customer segmentation and personalization
- Inventory management and restock alerts
- Review generation and social proof automation

REVENUE-DRIVING AUTOMATIONS:
- Abandoned cart recovery sequences (15min, 1hr, 24hr, 3day)
- Post-purchase upsell and cross-sell campaigns
- Review request automation with incentives
- Customer win-back campaigns for inactive users
- Inventory alerts and restock notifications
- Personalized product recommendations
- Birthday and anniversary promotions

PLATFORM EXPERTISE:
- Shopify, WooCommerce, BigCommerce integration
- Email marketing platforms (Mailchimp, Klaviyo)
- SMS marketing and customer communication
- Analytics and conversion tracking
- Payment processing and checkout optimization

SUCCESS METRICS:
- Conversion rate optimization
- Average order value increase
- Customer lifetime value growth
- Cart abandonment recovery rates
- Email/SMS open and click rates

COMMUNICATION STYLE:
- Revenue-focused and data-driven
- Provide specific ROI projections for automations
- Suggest A/B testing opportunities
- Focus on scalable growth strategies

Transform e-commerce stores into automated revenue-generating machines that work 24/7 to grow the business.""",
            
            model="gpt-4o-mini",
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ] + self.get_function_definitions()
        )
        
        self.created_assistants['ecommerce'] = assistant.id
        print(f"✅ Created E-commerce Assistant: {assistant.id}")
        return assistant.id
    
    async def create_healthcare_assistant(self):
        """Create specialized healthcare automation assistant"""
        print("🏥 Creating Healthcare Compliance Coordinator...")
        
        assistant = self.client.beta.assistants.create(
            name="Aiden Healthcare Compliance Coordinator",
            instructions="""You are Aiden, the HIPAA-compliant AI automation coordinator for healthcare practices.

CRITICAL RESPONSIBILITIES:
- Ensure ALL automations comply with HIPAA regulations
- Manage patient communication with complete privacy protection
- Coordinate appointment scheduling, reminders, and follow-ups
- Handle patient intake forms and insurance verification
- Maintain audit trails for all automated activities

HEALTHCARE COMPLIANCE:
- HIPAA privacy and security requirements
- Patient consent and communication preferences
- Secure messaging and protected health information (PHI)
- Audit trail maintenance and documentation
- Emergency vs routine communication protocols

PATIENT-CENTERED AUTOMATIONS:
- Appointment reminders with confirm/reschedule options
- Pre-visit paperwork and intake form delivery
- Post-visit care instructions and medication reminders
- Insurance verification and benefits checking
- Referral coordination and specialist scheduling
- Prescription refill reminders and pharmacy coordination
- Preventive care and wellness check reminders

COMPLIANCE FEATURES:
- All communications must be HIPAA compliant
- Use secure channels for sensitive health information
- Respect quiet hours and patient communication preferences
- Maintain detailed logs of all automated interactions
- Patient opt-out capabilities for all communications

HEALTHCARE WORKFLOWS:
- New patient onboarding and intake
- Appointment scheduling and management
- Insurance verification and prior authorization
- Lab results notification (secure channels only)
- Follow-up care coordination
- Patient satisfaction surveys

COMMUNICATION STYLE:
- Professional, caring, and compliant
- Patient privacy and safety as top priorities
- Clear explanations of compliance requirements
- Specific recommendations for secure automation
- Always verify compliance before implementing automations

Help healthcare practices improve patient care while maintaining complete regulatory compliance and protecting patient privacy.""",
            
            model="gpt-4o-mini", 
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ] + self.get_function_definitions()
        )
        
        self.created_assistants['healthcare'] = assistant.id
        print(f"✅ Created Healthcare Assistant: {assistant.id}")
        return assistant.id
    
    async def create_general_assistant(self):
        """Create general business automation consultant"""
        print("🚀 Creating General Business Automation Consultant...")
        
        assistant = self.client.beta.assistants.create(
            name="Aiden Business Automation Consultant",
            instructions="""You are Aiden, an expert AI business automation consultant helping businesses of all types build efficient automation systems.

YOUR EXPERTISE:
- Analyze business processes and identify automation opportunities
- Design custom automation workflows for any industry
- Recommend the best tools and integrations for specific needs
- Help businesses save time, reduce costs, and improve customer satisfaction

CORE CAPABILITIES:
- Business process analysis and optimization
- Customer communication automation (SMS, Email, Voice)
- Appointment scheduling and calendar management
- CRM integration and customer data management
- Task automation and workflow optimization
- Integration setup and API connections

AUTOMATION SPECIALTIES:
- Lead generation and nurturing
- Customer onboarding sequences
- Follow-up and retention campaigns
- Appointment booking and confirmations
- Invoice and payment processing
- Customer feedback collection
- Social media and marketing automation

CONSULTATION APPROACH:
1. Understand the business type and current processes
2. Identify repetitive tasks and inefficiencies
3. Recommend specific automation solutions
4. Provide implementation guidance and best practices
5. Suggest metrics to track automation success

COMMUNICATION STYLE:
- Ask detailed questions to understand business needs
- Provide specific, actionable recommendations
- Focus on ROI and business value
- Explain complex concepts in simple terms
- Always suggest next steps and implementation priorities

QUESTIONS TO ASK:
- What type of business do you run?
- What are your most time-consuming manual tasks?
- How do you currently communicate with customers?
- What tools and systems do you already use?
- What are your main business goals and challenges?

Help any business, regardless of industry, implement powerful automation systems that drive growth and efficiency.""",
            
            model="gpt-4o-mini",
            tools=[
                {"type": "code_interpreter"},
                {"type": "file_search"}
            ] + self.get_function_definitions()
        )
        
        self.created_assistants['general'] = assistant.id
        print(f"✅ Created General Business Assistant: {assistant.id}")
        return assistant.id
    
    async def create_all_assistants(self):
        """Create all specialized assistants"""
        print("🤖 CREATING AIDEN SUPERINTELLIGENCE ASSISTANTS")
        print("=" * 60)
        
        try:
            # Create all industry-specific assistants
            await self.create_hvac_assistant()
            await self.create_restaurant_assistant()
            await self.create_ecommerce_assistant()
            await self.create_healthcare_assistant()
            await self.create_general_assistant()
            
            print("\n" + "=" * 60)
            print("🎉 ALL ASSISTANTS CREATED SUCCESSFULLY!")
            print("=" * 60)
            
            # Save assistant IDs to file
            with open('assistant_ids.json', 'w') as f:
                json.dump(self.created_assistants, f, indent=2)
            
            print(f"📋 Assistant IDs saved to: assistant_ids.json")
            print("\n🔗 ASSISTANT DETAILS:")
            for industry, assistant_id in self.created_assistants.items():
                print(f"   {industry.upper()}: {assistant_id}")
            
            print("\n🚀 NEXT STEPS:")
            print("1. Update superintelligence.py with these assistant IDs")
            print("2. Test each assistant with demo_superintelligence.py")
            print("3. Your Control Tower now has specialized AI employees!")
            
            return self.created_assistants
            
        except Exception as e:
            print(f"❌ Error creating assistants: {e}")
            print("\n🔧 TROUBLESHOOTING:")
            print("1. Check your OpenAI API key in .env.local")
            print("2. Verify your account has Assistants API access")
            print("3. Ensure you have sufficient API credits")
            return {}

async def main():
    creator = AidenAssistantCreator()
    assistants = await creator.create_all_assistants()
    
    if assistants:
        print(f"\n✅ Created {len(assistants)} specialized assistants for Aiden SuperIntelligence!")
        
        # Show integration code
        print("\n📝 INTEGRATION CODE:")
        print("Add this to your superintelligence.py __init__ method:")
        print("```python")
        for industry, assistant_id in assistants.items():
            print(f"self.{industry}_assistant_id = \"{assistant_id}\"")
        print("```")

if __name__ == "__main__":
    asyncio.run(main())