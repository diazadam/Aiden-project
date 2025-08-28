#!/usr/bin/env python3
"""
LIST YOUR OPENAI ASSISTANTS
===========================

This script lists all assistants in your OpenAI account so you can find the correct ID
and integrate it with the Aiden SuperIntelligence system.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

def list_assistants():
    """List all your OpenAI Assistants"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    try:
        print("🔍 Listing all your OpenAI Assistants...")
        print("=" * 60)
        
        # List all assistants
        assistants = client.beta.assistants.list()
        
        if not assistants.data:
            print("❌ No assistants found in your account.")
            print("\n💡 NEXT STEPS:")
            print("1. Go to https://platform.openai.com/assistants")
            print("2. Create a new assistant or copy the ID of an existing one")
            print("3. Update the assistant ID in superintelligence.py")
        else:
            print(f"✅ Found {len(assistants.data)} assistant(s):")
            print()
            
            for i, assistant in enumerate(assistants.data, 1):
                print(f"🤖 Assistant {i}:")
                print(f"   ID: {assistant.id}")
                print(f"   Name: {assistant.name or 'Unnamed'}")
                print(f"   Model: {assistant.model}")
                print(f"   Tools: {[tool.type for tool in assistant.tools]}")
                print(f"   Created: {assistant.created_at}")
                print()
            
            # Show integration instructions
            print("🔗 TO INTEGRATE WITH AIDEN:")
            print("1. Copy the Assistant ID you want to use")
            print("2. Update this line in superintelligence.py:")
            print(f"   self.existing_assistant_id = \"YOUR_ASSISTANT_ID_HERE\"")
            print("3. Test with: python use_existing_assistant.py")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Check your OpenAI API key is correct in .env.local")
        print("2. Make sure your API key has access to the Assistants API")
        print("3. Verify you have created assistants in the OpenAI platform")

if __name__ == "__main__":
    list_assistants()