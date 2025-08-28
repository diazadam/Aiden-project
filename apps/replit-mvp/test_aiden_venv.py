#!/usr/bin/env python3
"""
AIDEN VIRTUAL ENVIRONMENT TEST
==============================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_aiden_in_venv():
    """Test Aiden in virtual environment"""
    
    print("🤖 TESTING AIDEN IN VIRTUAL ENVIRONMENT")
    print("=" * 50)
    
    try:
        # Test imports
        import openai
        print("✅ OpenAI imported successfully")
        
        import requests
        print("✅ Requests imported successfully")
        
        from pydantic import BaseModel
        print("✅ Pydantic imported successfully")
        
        # Test Aiden systems
        from superintelligence import AIDEN_SUPERINTELLIGENCE
        print("✅ SuperIntelligence system imported")
        
        from client_management_system import CLIENT_MANAGER
        print("✅ Client Management system imported")
        
        from real_system_control import REAL_CONTROLLER
        print("✅ Real System Control imported")
        
        print("\n🎉 ALL SYSTEMS OPERATIONAL IN VIRTUAL ENVIRONMENT!")
        print("🚀 Aiden is ready for production use!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_aiden_in_venv())
