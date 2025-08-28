#!/usr/bin/env python3
"""
Validation script to ensure Replit MVP is deployment-ready
Run this before deploying to Replit
"""
import sys
from pathlib import Path

def check_files():
    """Check all required files exist"""
    required_files = [
        "main.py",
        "requirements.txt", 
        ".env.example",
        ".replit",
        "replit.nix",
        "README.md",
        "public/index.html"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {missing}")
        return False
    else:
        print("✅ All required files present")
        return True

def check_imports():
    """Check all imports work"""
    try:
        import main
        print("✅ Main module imports successfully")
        
        from fastapi.testclient import TestClient
        client = TestClient(main.app)
        
        # Quick health check
        response = client.get("/api/health")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Quick chat test
        response = client.post("/api/chat", json={"message": "Hello test"})
        if response.status_code == 200:
            print("✅ Chat endpoint working")
        else:
            print(f"❌ Chat endpoint failed: {response.status_code}")
            return False
            
        return True
    except Exception as e:
        print(f"❌ Import/functionality error: {e}")
        return False

def check_config():
    """Check configuration templates"""
    try:
        with open(".env.example") as f:
            content = f.read()
            required_vars = ["OPENAI_API_KEY", "N8N_URL", "N8N_TOKEN"]
            missing = [var for var in required_vars if var not in content]
            if missing:
                print(f"❌ Missing env vars in template: {missing}")
                return False
            else:
                print("✅ Environment template complete")
                return True
    except Exception as e:
        print(f"❌ Config check failed: {e}")
        return False

def main():
    print("=== Aiden Replit MVP Validation ===\n")
    
    tests = [
        ("File structure", check_files),
        ("Imports & functionality", check_imports), 
        ("Configuration", check_config)
    ]
    
    all_pass = True
    for name, test_func in tests:
        print(f"Testing {name}:")
        if not test_func():
            all_pass = False
        print()
    
    if all_pass:
        print("🎉 ALL TESTS PASS - Ready for Replit deployment!")
        print("\nNext steps:")
        print("1. Upload this folder to new Replit Python project")
        print("2. Add API keys to Replit Secrets")
        print("3. Run: uvicorn main:app --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("❌ Some tests failed - fix issues before deploying")
        return 1

if __name__ == "__main__":
    sys.exit(main())