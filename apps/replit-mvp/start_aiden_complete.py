#!/usr/bin/env python3
"""
AIDEN COMPLETE SYSTEM STARTUP
=============================

This starts all Aiden systems in production mode.
"""

import os
import asyncio
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv()

async def start_aiden_complete_system():
    """Start all Aiden systems"""
    
    print("🤖 STARTING AIDEN COMPLETE SYSTEM")
    print("=" * 50)
    
    try:
        # Initialize all systems
        from superintelligence import AIDEN_SUPERINTELLIGENCE
        from client_management_system import CLIENT_MANAGER
        from real_system_control import REAL_CONTROLLER
        
        print("✅ SuperIntelligence: Online")
        print("✅ Client Manager: Online") 
        print("✅ Real System Control: Online")
        
        # Start health monitoring
        print("\n🔍 Starting health monitoring...")
        
        # Run initial health check
        health_results = await CLIENT_MANAGER.monitor_client_health()
        print(f"📊 Health check completed: {len(health_results)} clients monitored")
        
        print("\n🚀 AIDEN IS FULLY OPERATIONAL!")
        print("Ready for client automation and system control.")
        
        return True
        
    except Exception as e:
        print(f"❌ Startup failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(start_aiden_complete_system())
