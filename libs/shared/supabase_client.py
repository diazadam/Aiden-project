"""
Supabase Client for Server-Side Operations
==========================================

Server-side REST client for Aiden's Supabase project.
Uses SERVICE_ROLE key for full access - only use in secure server contexts.

Usage:
    from libs.shared.supabase_client import sb_upsert, sb_select, sb_update
    
    # Log a task execution
    await sb_upsert("tasks", {
        "trace_id": "abc123",
        "account_id": "adam", 
        "type": "voice_command",
        "payload": {"command": "open cursor"},
        "status": "completed"
    })
    
    # Query conversations
    rows = await sb_select("conversations", {"account_id": "adam"})
"""
import os, httpx, json
from typing import Any, Dict, List, Optional
from datetime import datetime

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_SERVICE_ROLE = (
    os.getenv("SUPABASE_SERVICE_ROLE_KEY") or 
    os.getenv("SUPABASE_JWT") or
    os.getenv("SUPABASE_SERVICE_ROLE")
)

def _get_headers():
    """Get headers for Supabase REST API"""
    if not SUPABASE_SERVICE_ROLE:
        raise RuntimeError("Supabase service role key not configured (SUPABASE_SERVICE_ROLE_KEY)")
    
    return {
        "apikey": SUPABASE_SERVICE_ROLE,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates,return=representation"
    }

async def sb_upsert(table: str, payload: Dict[str, Any], match_cols: Optional[List[str]] = None) -> tuple[int, str]:
    """
    Upsert data to Supabase table
    
    Args:
        table: Table name
        payload: Data to upsert
        match_cols: Columns to match on for upsert (defaults to primary key)
    
    Returns:
        (status_code, response_text)
    """
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    headers = _get_headers()
    
    # Add upsert parameters if match columns specified
    if match_cols:
        headers["Prefer"] += f",upsert={','.join(match_cols)}"
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.status_code, response.text
    except Exception as e:
        return 0, f"Request failed: {str(e)}"

async def sb_select(table: str, filters: Optional[Dict[str, Any]] = None, 
                   select: str = "*", limit: Optional[int] = None) -> List[Dict]:
    """
    Select data from Supabase table
    
    Args:
        table: Table name
        filters: WHERE clause filters (key=value pairs)
        select: Columns to select (default: all)
        limit: Maximum rows to return
    
    Returns:
        List of matching rows
    """
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {"select": select}
    
    # Add filters
    if filters:
        for key, value in filters.items():
            params[key] = f"eq.{value}"
    
    # Add limit
    if limit:
        params["limit"] = str(limit)
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(url, headers=_get_headers(), params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Supabase select error: {response.status_code} - {response.text}")
                return []
    except Exception as e:
        print(f"Supabase select failed: {e}")
        return []

async def sb_update(table: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> tuple[int, str]:
    """
    Update rows in Supabase table
    
    Args:
        table: Table name
        filters: WHERE clause filters 
        updates: Fields to update
    
    Returns:
        (status_code, response_text)
    """
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL not configured")
    
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    params = {}
    
    # Add filters
    for key, value in filters.items():
        params[key] = f"eq.{value}"
    
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.patch(url, headers=_get_headers(), params=params, json=updates)
            return response.status_code, response.text
    except Exception as e:
        return 0, f"Update failed: {str(e)}"

async def log_task_execution(trace_id: str, account_id: str, task_type: str, 
                           payload: Dict[str, Any], status: str = "completed", 
                           error: Optional[str] = None) -> bool:
    """
    Log a task execution to the tasks table
    
    Args:
        trace_id: Unique identifier for this execution
        account_id: User/account identifier
        task_type: Type of task (e.g., 'voice_command', 'host_executor')
        payload: Task details and parameters
        status: Execution status ('queued', 'completed', 'failed')
        error: Error message if status is 'failed'
    
    Returns:
        True if logged successfully
    """
    log_entry = {
        "trace_id": trace_id,
        "account_id": account_id,
        "type": task_type,
        "payload": payload,
        "status": status,
        "created_at": datetime.utcnow().isoformat()
    }
    
    if error:
        log_entry["error"] = error
    
    try:
        status_code, response = await sb_upsert("tasks", log_entry)
        return 200 <= status_code < 300
    except Exception as e:
        print(f"Failed to log task execution: {e}")
        return False

async def log_conversation(account_id: str, channel: str, transcript: List[Dict[str, Any]]) -> bool:
    """
    Log a conversation to the conversations table
    
    Args:
        account_id: User identifier
        channel: Channel/source (e.g., 'voice', 'chat', 'replit')
        transcript: List of messages with role/content
    
    Returns:
        True if logged successfully
    """
    conversation = {
        "account_id": account_id,
        "channel": channel,
        "transcript": transcript,
        "last_msg_at": datetime.utcnow().isoformat()
    }
    
    try:
        status_code, response = await sb_upsert("conversations", conversation)
        return 200 <= status_code < 300
    except Exception as e:
        print(f"Failed to log conversation: {e}")
        return False

# Synchronous versions for non-async contexts
def sync_upsert(table: str, payload: Dict[str, Any]) -> tuple[int, str]:
    """Synchronous version of sb_upsert"""
    import asyncio
    return asyncio.run(sb_upsert(table, payload))

def sync_select(table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict]:
    """Synchronous version of sb_select"""
    import asyncio
    return asyncio.run(sb_select(table, filters))

# Quick connection test
async def test_connection() -> bool:
    """Test Supabase connection"""
    try:
        await sb_select("tasks", limit=1)
        return True
    except Exception:
        return False