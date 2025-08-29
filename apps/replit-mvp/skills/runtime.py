"""
Skill runtime execution with sandboxing and capability enforcement.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
import tempfile
import time
import uuid
import shutil
from typing import Dict, Any, Optional
from pydantic import BaseModel
from .registry import REGISTRY
from .contracts import SkillContext, SkillOutputs

# Runtime configuration
SANDBOX_MODE = os.environ.get("AIDEN_SANDBOX_MODE", "inproc")
TIMEOUT_SEC  = int(os.environ.get("AIDEN_SKILL_TIMEOUT", "25"))

def _inproc_run(name: str, ctx: SkillContext, args: dict) -> SkillOutputs:
    """Run skill in the current process (Phase 2 v1)"""
    from security.policies import CapsPolicy, SECRET_PIN
    
    rs = REGISTRY.get(name)
    if not rs or not rs.enabled:
        return SkillOutputs(ok=False, message=f"Skill '{name}' not found/enabled")
    
    # Capability check
    if CapsPolicy.requires_pin(rs.manifest.caps) and ctx.caps_token != SECRET_PIN:
        return SkillOutputs(ok=False, message="PIN required for this skill capability.")
    
    try:
        # Validate args with skill schema
        inputs = rs.instance.Inputs(**args)
        return rs.instance.run(ctx, inputs)
    except Exception as e:
        return SkillOutputs(ok=False, message=f"Skill execution error: {str(e)}")

def run_skill(name: str, account_id: str, args: Dict[str, Any], caps_token: Optional[str] = None) -> SkillOutputs:
    """
    Execute a skill with the given parameters.
    
    Args:
        name: Skill name to execute
        account_id: User/account identifier for workspace isolation
        args: Arguments to pass to the skill
        caps_token: Capability token for elevated permissions
    
    Returns:
        SkillOutputs with execution results
    """
    # Create tenant-scoped working directory
    workdir = os.path.join("/tmp/aiden_work", account_id)
    os.makedirs(workdir, exist_ok=True)
    
    # Create execution context
    ctx = SkillContext(
        account_id=account_id, 
        workdir=workdir, 
        trace_id=str(uuid.uuid4()), 
        caps_token=caps_token
    )

    if SANDBOX_MODE == "inproc":
        return _inproc_run(name, ctx, args)

    # Future: Subprocess mode for untrusted code isolation
    # This would use a separate sandbox_runner.py script
    payload = {
        "name": name,
        "ctx": ctx.model_dump(),
        "args": args,
    }
    runner = os.path.join(os.path.dirname(__file__), "sandbox_runner.py")
    
    try:
        out = subprocess.run(
            [sys.executable, runner],
            input=json.dumps(payload).encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SEC,
            check=False,
        )
        if out.returncode != 0:
            return SkillOutputs(ok=False, message=f"Sandbox error: {out.stderr.decode()[:400]}")
        
        data = json.loads(out.stdout.decode())
        return SkillOutputs(**data)
        
    except subprocess.TimeoutExpired:
        return SkillOutputs(ok=False, message="Skill timed out")
    except Exception as e:
        return SkillOutputs(ok=False, message=f"Runtime error: {str(e)}")