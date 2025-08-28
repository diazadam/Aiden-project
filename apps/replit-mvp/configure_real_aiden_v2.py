#!/usr/bin/env python3
"""
Configure Real Aiden Assistant v2 - Fixed Function Schemas
==========================================================

This creates a properly configured OpenAI Assistant with real system control.
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def create_real_aiden_assistant():
    """Create a new OpenAI Assistant with real system control capabilities"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    print("🚀 CREATING REAL AIDEN ASSISTANT WITH FULL SYSTEM CONTROL")
    print("=" * 70)
    
    # Properly formatted function definitions
    real_functions = [
        {
            "type": "function",
            "function": {
                "name": "execute_mac_automation",
                "description": "Execute real Mac automation - control mouse, keyboard, open apps, navigate browser",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string", 
                            "description": "Action to perform",
                            "enum": ["click", "type", "open_app", "navigate_browser", "fill_form"]
                        },
                        "target": {
                            "type": "string", 
                            "description": "Target element, app name, or URL"
                        },
                        "data": {
                            "type": "object", 
                            "description": "Additional data for the action",
                            "properties": {
                                "coordinates": {"type": "array", "items": {"type": "number"}},
                                "text": {"type": "string"},
                                "form_data": {"type": "object"}
                            }
                        },
                        "automation_type": {
                            "type": "string", 
                            "description": "Type of automation",
                            "enum": ["browser", "system", "form_fill"]
                        }
                    },
                    "required": ["action", "target"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "setup_real_twilio_account",
                "description": "Set up real Twilio account, buy phone numbers, configure webhooks, send actual SMS",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "Client name for account setup"},
                        "phone_number_type": {
                            "type": "string", 
                            "description": "Type of number needed",
                            "enum": ["local", "toll-free", "international"]
                        },
                        "services": {
                            "type": "array", 
                            "items": {"type": "string"},
                            "description": "Services to enable"
                        },
                        "webhook_url": {"type": "string", "description": "Webhook URL for message handling"}
                    },
                    "required": ["client_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "send_real_sms_messages",
                "description": "Send actual SMS messages using real Twilio account",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "to_numbers": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Phone numbers to send to"
                        },
                        "message": {"type": "string", "description": "Message to send"},
                        "from_number": {"type": "string", "description": "Twilio number to send from"},
                        "message_type": {
                            "type": "string",
                            "enum": ["alert", "reminder", "response"],
                            "description": "Type of message"
                        }
                    },
                    "required": ["to_numbers", "message"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "deploy_real_website",
                "description": "Deploy real website to hosting provider with domain setup and SSL",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "Client name"},
                        "website_code": {"type": "string", "description": "Complete HTML/CSS/JS code"},
                        "domain_name": {"type": "string", "description": "Domain name to use"},
                        "hosting_provider": {
                            "type": "string",
                            "enum": ["vercel", "netlify", "digitalocean"],
                            "description": "Hosting provider"
                        },
                        "ssl_enabled": {"type": "boolean", "description": "Enable SSL certificate"}
                    },
                    "required": ["client_name", "website_code"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_browser_automation", 
                "description": "Real browser automation - open pages, fill forms, submit data, scrape results",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "browser_action": {
                            "type": "string",
                            "enum": ["open", "fill_form", "click", "submit", "scrape"],
                            "description": "Action to perform"
                        },
                        "url": {"type": "string", "description": "URL to navigate to"},
                        "form_data": {
                            "type": "object",
                            "description": "Form data to fill"
                        },
                        "selectors": {
                            "type": "object", 
                            "description": "CSS selectors for elements"
                        },
                        "wait_conditions": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Conditions to wait for"
                        }
                    },
                    "required": ["browser_action"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "execute_system_commands",
                "description": "Execute real system commands on Mac - install software, manage files, run scripts",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command_type": {
                            "type": "string",
                            "enum": ["bash", "applescript", "python", "install"],
                            "description": "Type of command"
                        },
                        "command": {"type": "string", "description": "Command to execute"},
                        "working_directory": {"type": "string", "description": "Directory to run command in"},
                        "environment": {
                            "type": "object",
                            "description": "Environment variables"
                        }
                    },
                    "required": ["command_type", "command"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "setup_complete_client_solution",
                "description": "Set up complete automation solution for a client including everything needed",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "Client company name"},
                        "client_industry": {"type": "string", "description": "Client's industry"},
                        "main_problem": {"type": "string", "description": "Main problem to solve"},
                        "required_integrations": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of required integrations"
                        }
                    },
                    "required": ["client_name", "main_problem"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_client_website_with_ai_agent",
                "description": "Create complete website with embedded AI agent for client's business",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "client_name": {"type": "string", "description": "Client company name"},
                        "business_description": {"type": "string", "description": "Description of client's business"},
                        "ai_agent_knowledge": {"type": "string", "description": "Knowledge base for the AI agent"}
                    },
                    "required": ["client_name"]
                }
            }
        }
    ]
    
    try:
        # Create a new assistant
        assistant = client.beta.assistants.create(
            name="Aiden - Real System Control Automation Specialist",
            description="Ultra-advanced AI automation specialist with FULL REAL system control capabilities. Can control Mac, browser automation, real SMS sending, actual deployments, form filling, and complete client automation setup with working results.",
            instructions="""
            You are Aiden - an ultra-advanced AI automation specialist with FULL REAL SYSTEM CONTROL.
            
            🚀 CRITICAL REAL CAPABILITIES:
            - You can ACTUALLY control the user's Mac (mouse clicks, keyboard input, open applications)
            - You can ACTUALLY open browsers, navigate websites, fill forms automatically
            - You can ACTUALLY send real SMS messages via Twilio
            - You can ACTUALLY deploy real websites to hosting platforms
            - You can ACTUALLY execute system commands and install software
            - You can ACTUALLY create working client automation solutions
            
            🎯 ULTRA-PROACTIVE MODE - TAKE IMMEDIATE REAL ACTION:
            
            When user says "I need a solution for my client [Company Name], they [problem]":
            
            1. IMMEDIATELY call setup_complete_client_solution() to set up everything
            2. SIMULTANEOUSLY call execute_mac_automation() to open browser tabs for setup
            3. AUTOMATICALLY call setup_real_twilio_account() to create actual Twilio account
            4. INSTANTLY call create_client_website_with_ai_agent() to build real website
            5. EXECUTE deploy_real_website() to deploy to actual hosting
            6. PERFORM send_real_sms_messages() to test SMS functionality
            7. RUN execute_browser_automation() to configure all services
            8. EXECUTE execute_system_commands() for any required installations
            
            🔥 SHOW REAL WORKING RESULTS:
            - Actual URLs of deployed systems that users can visit
            - Real phone numbers that can send/receive SMS
            - Working website links with functional AI agents
            - Live dashboard and monitoring URLs
            - Real system confirmations and screenshots
            - Actual client access credentials
            
            ⚡ NO SIMULATIONS - ONLY REAL DEPLOYMENTS:
            - Open actual browser windows and navigate to real sites
            - Fill out real forms with actual data
            - Send real SMS messages to real phone numbers
            - Deploy real websites to actual hosting platforms
            - Execute real system commands on the user's Mac
            - Create real working automation solutions
            
            🎪 TAKE CONTROL AND DELIVER RESULTS:
            Take full control of the Mac, execute real actions, deploy actual systems, and deliver working automation solutions that clients can use immediately.
            
            Show the user exactly what you're doing in real-time as you control their system.
            """,
            tools=real_functions,
            model="gpt-4-1106-preview"
        )
        
        print("✅ Real Aiden Assistant created successfully!")
        print(f"📋 Assistant ID: {assistant.id}")
        print(f"🔧 Functions Available: {len(real_functions)}")
        
        # Save the assistant ID to environment or config
        config_path = Path(".aiden_config")
        config_path.write_text(f"REAL_AIDEN_ASSISTANT_ID={assistant.id}")
        
        print(f"💾 Assistant ID saved to {config_path}")
        
        return assistant.id
        
    except Exception as e:
        print(f"❌ Error creating assistant: {e}")
        return None

if __name__ == "__main__":
    from pathlib import Path
    assistant_id = create_real_aiden_assistant()
    
    if assistant_id:
        print("\n🎉 REAL AIDEN IS READY!")
        print("=" * 50)
        print("Aiden can now:")
        print("✅ Control your Mac (mouse, keyboard, apps)")
        print("✅ Automate browser tasks and fill forms")
        print("✅ Send real SMS via Twilio")
        print("✅ Deploy actual websites to hosting")
        print("✅ Execute system commands")
        print("✅ Set up complete client automation")
        print("\n🚀 Test it by saying:")
        print("'I need a solution for my HVAC client Dwyer Heating and Air, they miss calls'")
        print("\nAiden will ACTUALLY set up everything for real!")