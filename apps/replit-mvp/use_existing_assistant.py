#!/usr/bin/env python3
"""
USE YOUR EXISTING OPENAI ASSISTANT
=================================

This script shows how to use your existing OpenAI Assistant (asst_mmCt54r7HpOgR5hQFaNhyDks)
with the Aiden SuperIntelligence system.
"""

import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment
load_dotenv()

async def test_your_assistant():
    """Test conversation with your existing OpenAI Assistant"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    assistant_id = "asst_mmCt54r7HpOgR5hQFaNhyDks"  # Your assistant ID
    
    print("🤖 Testing your OpenAI Assistant...")
    print(f"Assistant ID: {assistant_id}")
    
    try:
        # Get assistant details
        assistant = client.beta.assistants.retrieve(assistant_id)
        print(f"✅ Assistant Name: {assistant.name}")
        print(f"✅ Model: {assistant.model}")
        print(f"✅ Tools: {[tool.type for tool in assistant.tools]}")
        
        # Create a conversation thread
        thread = client.beta.threads.create()
        print(f"✅ Created thread: {thread.id}")
        
        # Send a test message
        message = "Hello! Can you help me set up automation for my business?"
        
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message
        )
        
        # Run the assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )
        
        # Wait for completion
        while run.status in ["queued", "in_progress"]:
            await asyncio.sleep(1)
            run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        
        if run.status == "completed":
            # Get the response
            messages = client.beta.threads.messages.list(thread_id=thread.id)
            latest_message = messages.data[0]
            response = latest_message.content[0].text.value
            
            print(f"\n👤 You: {message}")
            print(f"🤖 Assistant: {response}")
            
        else:
            print(f"❌ Run failed with status: {run.status}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

async def integrate_with_aiden():
    """Show how to integrate your assistant with Aiden SuperIntelligence"""
    
    print("\n" + "="*60)
    print("🔗 INTEGRATING YOUR ASSISTANT WITH AIDEN")
    print("="*60)
    
    integration_code = '''
# Add this to your superintelligence.py to use your existing assistant:

async def use_existing_assistant(self, assistant_id: str, message: str):
    """Use an existing OpenAI Assistant instead of creating new ones"""
    
    # Create or reuse conversation thread  
    thread = self.client.beta.threads.create()
    
    # Add user message
    self.client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user", 
        content=message
    )
    
    # Run your assistant
    run = self.client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id  # Your assistant: asst_mmCt54r7HpOgR5hQFaNhyDks
    )
    
    # Wait for completion and return response
    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(1)
        run = self.client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == "completed":
        messages = self.client.beta.threads.messages.list(thread_id=thread.id)
        return messages.data[0].content[0].text.value
    
    return f"Assistant run failed: {run.status}"
'''
    
    print(integration_code)
    
    print("\n🎯 INTEGRATION OPTIONS:")
    print("1. Use your assistant as the default for all conversations")
    print("2. Use your assistant for specific business types")  
    print("3. Create a hybrid system with both custom and your assistants")
    print("\nYour assistant ID: asst_mmCt54r7HpOgR5hQFaNhyDks")

if __name__ == "__main__":
    asyncio.run(test_your_assistant())
    asyncio.run(integrate_with_aiden())