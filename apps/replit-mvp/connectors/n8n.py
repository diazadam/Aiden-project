"""
AidenAI n8n Connector - Workflow automation via webhooks for 350+ integrations
"""
from __future__ import annotations
import os
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime

class N8NConnector:
    """Connector for n8n workflow automation platform"""
    
    def __init__(self):
        self.webhook_base = os.environ.get("N8N_WEBHOOK_BASE", "").rstrip("/")
        self.api_key = os.environ.get("N8N_API_KEY")
        self.timeout = 30.0
        
    def is_available(self) -> bool:
        """Check if n8n connector is properly configured"""
        return bool(self.webhook_base)
    
    async def trigger_webhook(self, webhook_path: str, data: Dict[str, Any], 
                            method: str = "POST") -> Dict[str, Any]:
        """Trigger an n8n webhook with provided data"""
        if not self.is_available():
            return {"ok": False, "message": "N8N_WEBHOOK_BASE not configured"}
        
        url = f"{self.webhook_base}/{webhook_path.lstrip('/')}"
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=data)
                else:
                    response = await client.request(method.upper(), url, json=data, headers=headers)
                
                result = {
                    "ok": response.status_code < 400,
                    "status_code": response.status_code,
                    "url": url,
                    "timestamp": datetime.now().isoformat()
                }
                
                try:
                    result["data"] = response.json()
                except:
                    result["data"] = response.text
                
                if not result["ok"]:
                    result["message"] = f"HTTP {response.status_code}: {response.text[:200]}"
                else:
                    result["message"] = f"Webhook triggered successfully"
                
                return result
                
        except Exception as e:
            return {
                "ok": False,
                "message": f"Webhook trigger failed: {str(e)}",
                "url": url,
                "error": str(e)
            }
    
    async def send_notification(self, message: str, channel: str = "general", 
                               urgency: str = "normal") -> Dict[str, Any]:
        """Send notification via n8n workflow"""
        return await self.trigger_webhook("notify", {
            "message": message,
            "channel": channel,
            "urgency": urgency,
            "source": "aiden_ai",
            "timestamp": datetime.now().isoformat()
        })
    
    async def process_data(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process data through an n8n workflow"""
        return await self.trigger_webhook(f"process/{workflow_id}", {
            "input": input_data,
            "source": "aiden_ai",
            "timestamp": datetime.now().isoformat()
        })
    
    async def create_task(self, title: str, description: str = "", 
                         assignee: str = "", priority: str = "normal") -> Dict[str, Any]:
        """Create a task via n8n workflow integration"""
        return await self.trigger_webhook("tasks/create", {
            "title": title,
            "description": description,
            "assignee": assignee,
            "priority": priority,
            "source": "aiden_ai",
            "created_at": datetime.now().isoformat()
        })
    
    async def update_crm(self, contact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update CRM system via n8n workflow"""
        return await self.trigger_webhook("crm/contact", {
            "contact": contact_data,
            "source": "aiden_ai",
            "updated_at": datetime.now().isoformat()
        })
    
    async def send_email(self, to: str, subject: str, content: str, 
                        template: str = None) -> Dict[str, Any]:
        """Send email via n8n workflow"""
        email_data = {
            "to": to,
            "subject": subject,
            "content": content,
            "source": "aiden_ai",
            "sent_at": datetime.now().isoformat()
        }
        
        if template:
            email_data["template"] = template
        
        return await self.trigger_webhook("email/send", email_data)
    
    async def sync_calendar(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync calendar event via n8n workflow"""
        return await self.trigger_webhook("calendar/event", {
            "event": event_data,
            "source": "aiden_ai",
            "timestamp": datetime.now().isoformat()
        })
    
    async def backup_data(self, data: Dict[str, Any], backup_type: str = "general") -> Dict[str, Any]:
        """Backup data via n8n workflow"""
        return await self.trigger_webhook("backup/create", {
            "data": data,
            "backup_type": backup_type,
            "source": "aiden_ai",
            "timestamp": datetime.now().isoformat()
        })
    
    def get_webhook_url(self, path: str) -> str:
        """Get full webhook URL for a given path"""
        if not self.webhook_base:
            return ""
        return f"{self.webhook_base}/{path.lstrip('/')}"
    
    def build_webhook_payload(self, event_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Build standardized webhook payload"""
        return {
            "event_type": event_type,
            "source": "aiden_ai",
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "metadata": {
                "version": "2.0",
                "sdk": "aiden_ai_power_stack"
            }
        }

# Global n8n connector instance
n8n = N8NConnector()

# Convenience functions for common operations
async def notify(message: str, channel: str = "general") -> Dict[str, Any]:
    """Quick notification function"""
    return await n8n.send_notification(message, channel)

async def create_task(title: str, description: str = "") -> Dict[str, Any]:
    """Quick task creation function"""
    return await n8n.create_task(title, description)

async def trigger_workflow(webhook_path: str, data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick workflow trigger function"""
    return await n8n.trigger_webhook(webhook_path, data)