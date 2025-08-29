#!/usr/bin/env python3
"""
Quick test script to verify Aiden is accessible
"""
import requests
import webbrowser
import sys
import time

def test_aiden_access():
    base_url = "http://localhost:8000"
    
    print("🤖 Testing Aiden Access...")
    print("-" * 50)
    
    # Test API health
    try:
        print("1. Testing API health...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API: {data.get('app', 'Unknown')} ({data.get('provider', 'Unknown')})")
        else:
            print(f"   ❌ API returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API connection failed: {e}")
        return False
    
    # Test web interface
    try:
        print("2. Testing web interface...")
        response = requests.get(f"{base_url}/app/", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ Web interface accessible")
        else:
            print(f"   ❌ Web interface returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Web interface connection failed: {e}")
    
    # Test ChatGPT-style interface
    try:
        print("3. Testing ChatGPT-style interface...")
        response = requests.get(f"{base_url}/app/chatgpt-style.html", timeout=5)
        if response.status_code == 200:
            print(f"   ✅ ChatGPT-style interface accessible")
        else:
            print(f"   ❌ ChatGPT-style interface returned status {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ ChatGPT-style interface connection failed: {e}")
    
    print("-" * 50)
    print("🚀 Opening Aiden interfaces...")
    
    # Open the interfaces
    urls_to_open = [
        (f"{base_url}/app/", "Main Control Tower"),
        (f"{base_url}/app/chatgpt-style.html", "ChatGPT-Style Chat")
    ]
    
    for url, name in urls_to_open:
        print(f"   Opening {name}: {url}")
        webbrowser.open(url)
        time.sleep(1)  # Small delay between opens
    
    print("✅ Aiden interfaces opened in your browser!")
    print("")
    print("🎯 Quick Test Commands:")
    print("   • Clone a website: 'clone https://github.com'")
    print("   • Deploy to cloud: 'deploy my-awesome-app'")
    print("   • Create iOS app: 'ios create RestaurantApp'")
    print("   • Generate demo: 'create ad'")
    print("")
    
    return True

if __name__ == "__main__":
    success = test_aiden_access()
    if not success:
        print("❌ Aiden is not accessible. Try running:")
        print("   cd ~/aiden-project && make run-ctl")
        sys.exit(1)
    else:
        print("🤖 Aiden is ready to help!")