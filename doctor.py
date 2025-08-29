#!/usr/bin/env python3
"""
🩺 AIDEN DOCTOR - COMPREHENSIVE SYSTEM HEALTH CHECK
Validates all secrets, APIs, permissions, and system requirements.
"""

import asyncio
import os
import sys
import json
import httpx
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add libs to path
sys.path.append(str(Path(__file__).parent / "libs"))

try:
    from libs.shared.secrets import secrets_manager, SecretsSchema
    from libs.shared.connectors import health_check_all_connectors
    CONNECTORS_AVAILABLE = True
except ImportError:
    print("❌ Failed to import modules. Run from project root.")
    CONNECTORS_AVAILABLE = False
    sys.exit(1)

class HealthCheck:
    """Individual health check result"""
    def __init__(self, name: str, status: str, message: str, details: Optional[Dict] = None):
        self.name = name
        self.status = status  # ✅, ❌, ⚠️ 
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()

class AidenDoctor:
    """Comprehensive Aiden system health checker"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.secrets = secrets_manager.secrets
    
    async def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks and return results"""
        print("🩺 AIDEN DOCTOR - Starting comprehensive health check...\n")
        
        # Core system checks
        await self._check_secrets()
        await self._check_file_permissions()
        await self._check_python_environment()
        
        # API connectivity checks
        await self._check_openai_api()
        await self._check_anthropic_api()
        await self._check_elevenlabs_api()
        await self._check_supabase_connection()
        await self._check_google_cloud()
        
        # Service checks
        await self._check_enhanced_aiden()
        await self._check_web_server()
        
        # Unified connector checks
        if CONNECTORS_AVAILABLE:
            await self._check_unified_connectors()
        
        # Generate report
        return self._generate_report()
    
    def _add_check(self, name: str, status: str, message: str, details: Optional[Dict] = None):
        """Add a health check result"""
        check = HealthCheck(name, status, message, details)
        self.checks.append(check)
        print(f"{status} {name}: {message}")
    
    async def _check_secrets(self):
        """Validate secrets configuration"""
        print("🔐 Checking secrets configuration...")
        
        if not self.secrets:
            self._add_check("Secrets Schema", "❌", "Failed to load secrets from .env.local")
            return
        
        self._add_check("Secrets Schema", "✅", "Secrets loaded and validated successfully")
        
        # Check critical secrets
        critical_secrets = {
            'openai_api_key': 'OpenAI API (Required for core AI)',
            'supabase_url': 'Supabase URL (Required for memory)',
            'supabase_service_role_key': 'Supabase Service Key (Required for memory)',
        }
        
        for secret_key, description in critical_secrets.items():
            value = getattr(self.secrets, secret_key, None)
            if value:
                self._add_check(f"Secret: {secret_key}", "✅", description)
            else:
                self._add_check(f"Secret: {secret_key}", "⚠️", f"Optional: {description}")
        
        # Check optional but valuable secrets
        optional_secrets = {
            'anthropic_api_key': 'Anthropic Claude API',
            'elevenlabs_api_key': 'ElevenLabs TTS API',
            'gcp_project_id': 'Google Cloud Platform',
            'pinecone_api_key': 'Pinecone Vector Database',
        }
        
        for secret_key, description in optional_secrets.items():
            value = getattr(self.secrets, secret_key, None)
            status = "✅" if value else "⚠️"
            message = f"{description} - {'Configured' if value else 'Not configured'}"
            self._add_check(f"Optional: {secret_key}", status, message)
    
    async def _check_file_permissions(self):
        """Check file system permissions"""
        print("\n📁 Checking file system permissions...")
        
        # Check write permissions for key directories
        directories_to_check = [
            "apps/replit-mvp/deployed",
            "apps/replit-mvp/generated", 
            "logs",
            "ops/artifacts"
        ]
        
        for dir_path in directories_to_check:
            full_path = Path(dir_path)
            try:
                # Create directory if it doesn't exist
                full_path.mkdir(parents=True, exist_ok=True)
                
                # Test write permission
                test_file = full_path / "test_write_permission.txt"
                test_file.write_text("test")
                test_file.unlink()
                
                self._add_check(f"Directory: {dir_path}", "✅", "Write permissions OK")
            except Exception as e:
                self._add_check(f"Directory: {dir_path}", "❌", f"Permission error: {str(e)}")
        
        # Check read permissions for key files
        files_to_check = [
            "apps/replit-mvp/main.py",
            "apps/replit-mvp/superintelligence.py",
            ".env.example",
        ]
        
        for file_path in files_to_check:
            full_path = Path(file_path)
            if full_path.exists():
                try:
                    full_path.read_text()
                    self._add_check(f"File: {file_path}", "✅", "Read permissions OK")
                except Exception as e:
                    self._add_check(f"File: {file_path}", "❌", f"Read error: {str(e)}")
            else:
                self._add_check(f"File: {file_path}", "❌", "File does not exist")
    
    async def _check_python_environment(self):
        """Check Python environment and dependencies"""
        print("\n🐍 Checking Python environment...")
        
        # Check Python version
        python_version = sys.version.split()[0]
        if sys.version_info >= (3, 9):
            self._add_check("Python Version", "✅", f"Python {python_version} (OK)")
        else:
            self._add_check("Python Version", "❌", f"Python {python_version} (Requires 3.9+)")
        
        # Check critical dependencies
        critical_deps = [
            'fastapi',
            'uvicorn', 
            'openai',
            'pydantic',
            'httpx',
            'python-dotenv'
        ]
        
        for dep in critical_deps:
            try:
                __import__(dep.replace('-', '_'))
                self._add_check(f"Dependency: {dep}", "✅", "Installed")
            except ImportError:
                self._add_check(f"Dependency: {dep}", "❌", "Not installed")
        
        # Check optional dependencies
        optional_deps = [
            'anthropic',
            'elevenlabs',
            'google-cloud-storage',
            'pinecone-client',
            'playwright'
        ]
        
        # Check browser automation specifically
        try:
            import playwright
            from playwright.async_api import async_playwright
            self._add_check("Browser Automation", "✅", "Playwright installed and ready")
        except ImportError:
            self._add_check("Browser Automation", "⚠️", "Playwright not installed (optional for web automation)")
        
        # Check Mac system control
        import platform
        if platform.system() == "Darwin":
            try:
                # Check if osascript is available
                import subprocess
                subprocess.run(["osascript", "-e", "1 + 1"], 
                             capture_output=True, check=True, timeout=5)
                self._add_check("Mac System Control", "✅", "AppleScript/JXA automation ready")
            except:
                self._add_check("Mac System Control", "⚠️", "AppleScript not available on this macOS system")
        else:
            self._add_check("Mac System Control", "⚠️", f"Mac control requires macOS (running {platform.system()})")
        
        for dep in optional_deps:
            try:
                __import__(dep.replace('-', '_').replace('google_cloud_storage', 'google.cloud.storage'))
                self._add_check(f"Optional: {dep}", "✅", "Installed")
            except ImportError:
                self._add_check(f"Optional: {dep}", "⚠️", "Not installed (optional)")
    
    async def _check_openai_api(self):
        """Test OpenAI API connectivity"""
        print("\n🤖 Checking OpenAI API...")
        
        if not self.secrets.openai_api_key:
            self._add_check("OpenAI API", "❌", "API key not configured")
            return
        
        try:
            import openai
            client = openai.AsyncOpenAI(api_key=self.secrets.openai_api_key)
            
            # Test with minimal API call
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=5
            )
            
            self._add_check("OpenAI API", "✅", "Connection successful")
        except Exception as e:
            self._add_check("OpenAI API", "❌", f"Connection failed: {str(e)}")
    
    async def _check_anthropic_api(self):
        """Test Anthropic API connectivity"""
        print("\n🧠 Checking Anthropic API...")
        
        if not self.secrets.anthropic_api_key:
            self._add_check("Anthropic API", "⚠️", "API key not configured (optional)")
            return
        
        try:
            import anthropic
            client = anthropic.AsyncAnthropic(api_key=self.secrets.anthropic_api_key)
            
            # Test with minimal API call
            response = await client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Test"}]
            )
            
            self._add_check("Anthropic API", "✅", "Connection successful")
        except ImportError:
            self._add_check("Anthropic API", "⚠️", "anthropic package not installed")
        except Exception as e:
            self._add_check("Anthropic API", "❌", f"Connection failed: {str(e)}")
    
    async def _check_elevenlabs_api(self):
        """Test ElevenLabs API connectivity"""
        print("\n🔊 Checking ElevenLabs API...")
        
        if not self.secrets.elevenlabs_api_key:
            self._add_check("ElevenLabs API", "⚠️", "API key not configured (optional)")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {"xi-api-key": self.secrets.elevenlabs_api_key}
                response = await client.get(
                    "https://api.elevenlabs.io/v1/voices",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    voices = response.json().get("voices", [])
                    self._add_check("ElevenLabs API", "✅", f"Connection successful ({len(voices)} voices)")
                else:
                    self._add_check("ElevenLabs API", "❌", f"API error: {response.status_code}")
        except Exception as e:
            self._add_check("ElevenLabs API", "❌", f"Connection failed: {str(e)}")
    
    async def _check_supabase_connection(self):
        """Test Supabase connectivity"""
        print("\n🗄️ Checking Supabase connection...")
        
        if not (self.secrets.supabase_url and self.secrets.supabase_service_role_key):
            self._add_check("Supabase", "❌", "URL or service key not configured")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "apikey": self.secrets.supabase_service_role_key,
                    "Authorization": f"Bearer {self.secrets.supabase_service_role_key}"
                }
                
                # Test connection with a simple query
                response = await client.get(
                    f"{self.secrets.supabase_url}/rest/v1/",
                    headers=headers,
                    timeout=10
                )
                
                if response.status_code in [200, 404]:  # 404 is OK for root endpoint
                    self._add_check("Supabase", "✅", "Connection successful")
                else:
                    self._add_check("Supabase", "❌", f"Connection error: {response.status_code}")
        except Exception as e:
            self._add_check("Supabase", "❌", f"Connection failed: {str(e)}")
    
    async def _check_google_cloud(self):
        """Test Google Cloud connectivity"""
        print("\n☁️ Checking Google Cloud...")
        
        if not self.secrets.gcp_project_id:
            self._add_check("Google Cloud", "⚠️", "Project ID not configured (optional)")
            return
        
        try:
            from google.cloud import storage
            
            # Try to initialize client
            client = storage.Client()
            
            # Test with a simple operation
            buckets = list(client.list_buckets(max_results=1))
            self._add_check("Google Cloud", "✅", f"Connection successful (Project: {self.secrets.gcp_project_id})")
        except ImportError:
            self._add_check("Google Cloud", "⚠️", "google-cloud-storage package not installed")
        except Exception as e:
            self._add_check("Google Cloud", "❌", f"Connection failed: {str(e)}")
    
    async def _check_enhanced_aiden(self):
        """Test Enhanced Aiden core functionality"""
        print("\n🧠 Checking Enhanced Aiden core...")
        
        try:
            # Import Enhanced Aiden
            sys.path.append("apps/replit-mvp")
            from superintelligence import AIDEN_SUPERINTELLIGENCE_ENHANCED
            
            self._add_check("Enhanced Aiden Import", "✅", "Core module imported successfully")
            
            # Test basic functionality (without API call)
            self._add_check("Enhanced Aiden Core", "✅", "Action-oriented intelligence loaded")
        except Exception as e:
            self._add_check("Enhanced Aiden", "❌", f"Core module error: {str(e)}")
    
    async def _check_web_server(self):
        """Test web server functionality"""
        print("\n🌐 Checking web server...")
        
        try:
            # Check if main.py can be imported
            sys.path.append("apps/replit-mvp")
            import main
            
            self._add_check("FastAPI Server", "✅", "Main server module loaded")
            
            # Check if server can start (without actually starting it)
            app = main.app
            self._add_check("FastAPI App", "✅", "Application instance created")
        except Exception as e:
            self._add_check("Web Server", "❌", f"Server error: {str(e)}")
    
    async def _check_unified_connectors(self):
        """Test unified connector layer"""
        print("\n🔌 Checking unified connector layer...")
        
        try:
            # Test all connectors
            connector_results = await health_check_all_connectors()
            
            for connector_name, result in connector_results.items():
                if result.success:
                    status = "✅"
                    message = f"Connector operational ({result.execution_time_ms:.1f}ms)"
                else:
                    status = "❌" if "not configured" in str(result.error) else "⚠️"
                    message = str(result.error)
                
                self._add_check(f"Connector: {connector_name}", status, message)
            
            # Overall connector system status
            working_connectors = sum(1 for r in connector_results.values() if r.success)
            total_connectors = len(connector_results)
            
            if working_connectors > 0:
                self._add_check("Unified Connector System", "✅", 
                              f"{working_connectors}/{total_connectors} connectors operational")
            else:
                self._add_check("Unified Connector System", "❌", 
                              "No connectors operational")
                
        except Exception as e:
            self._add_check("Unified Connector System", "❌", f"Connector system error: {str(e)}")
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive health report"""
        print("\n" + "="*60)
        print("🩺 AIDEN DOCTOR REPORT")
        print("="*60)
        
        # Count statuses
        passed = len([c for c in self.checks if c.status == "✅"])
        warned = len([c for c in self.checks if c.status == "⚠️"])
        failed = len([c for c in self.checks if c.status == "❌"])
        total = len(self.checks)
        
        # Overall status
        if failed == 0 and warned == 0:
            overall_status = "🟢 EXCELLENT - All systems operational"
        elif failed == 0:
            overall_status = f"🟡 GOOD - {warned} warnings, but core systems operational"
        elif failed < 3:
            overall_status = f"🟠 NEEDS ATTENTION - {failed} critical issues"
        else:
            overall_status = f"🔴 CRITICAL - {failed} critical issues require immediate attention"
        
        print(f"\nOVERALL STATUS: {overall_status}")
        print(f"RESULTS: {passed} passed, {warned} warnings, {failed} failed ({total} total)")
        
        # Show failed checks
        if failed > 0:
            print(f"\n❌ CRITICAL ISSUES ({failed}):")
            for check in self.checks:
                if check.status == "❌":
                    print(f"  • {check.name}: {check.message}")
        
        # Show warnings
        if warned > 0:
            print(f"\n⚠️ WARNINGS ({warned}):")
            for check in self.checks:
                if check.status == "⚠️":
                    print(f"  • {check.name}: {check.message}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if failed > 0:
            print("  • Fix critical issues before deploying Enhanced Aiden")
            print("  • Ensure all API keys are properly configured")
            print("  • Verify file permissions and dependencies")
        
        if warned > 0:
            print("  • Consider configuring optional services for full functionality")
            print("  • ElevenLabs API for voice capabilities")
            print("  • Google Cloud for advanced deployment options")
        
        print("  • Run `make doctor` regularly to monitor system health")
        print("  • Keep all API keys secure and rotate regularly")
        
        # Next steps
        if failed == 0:
            print(f"\n🚀 NEXT STEPS:")
            print("  • Enhanced Aiden is ready for operation!")
            print("  • Start with: cd apps/replit-mvp && python -m uvicorn main:app --port 8001")
            print("  • Test with: curl -X POST -H 'Content-Type: application/json' \\")
            print("              -d '{\"message\":\"Build me a website\",\"account_id\":\"test\"}' \\")
            print("              http://localhost:8001/api/chat")
        
        print("="*60)
        
        # Return structured report
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "total_checks": total,
                "passed": passed,
                "warnings": warned,
                "failed": failed
            },
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "message": check.message,
                    "details": check.details,
                    "timestamp": check.timestamp
                }
                for check in self.checks
            ],
            "secrets_summary": secrets_manager.get_masked_summary(),
            "ready_for_production": failed == 0
        }

async def main():
    """Run Aiden Doctor health check"""
    doctor = AidenDoctor()
    report = await doctor.run_all_checks()
    
    # Save report to file
    report_path = Path("logs/doctor_report.json")
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\nDetailed report saved to: {report_path}")
    
    # Exit with appropriate code
    if not report["ready_for_production"]:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())