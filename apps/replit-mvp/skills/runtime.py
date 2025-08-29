"""
Skills runtime engine with subprocess isolation and network gating.

Provides secure skill execution with:
- Subprocess isolation by default (configurable via AIDEN_SANDBOX_MODE)
- Network blocking unless skill declares 'net' capability
- Resource limits and timeout enforcement
- Capability-based security with PIN requirements
"""
from __future__ import annotations
import json, os, subprocess, sys, uuid, shutil
from typing import Dict, Any, Optional
from .registry import REGISTRY
from .contracts import SkillContext, SkillOutputs
from security.policies import CapsPolicy, SECRET_PIN

SANDBOX_MODE = os.environ.get("AIDEN_SANDBOX_MODE", "subprocess")
TIMEOUT_SEC  = int(os.environ.get("AIDEN_SKILL_TIMEOUT", "30"))

def _inproc_run(name: str, ctx: SkillContext, args: dict) -> SkillOutputs:
    """Run skill in the current process (legacy mode)"""
    rs = REGISTRY.get(name)
    if not rs or not rs.enabled:
        return SkillOutputs(ok=False, message=f"Skill '{name}' not found/enabled")
    
    # PIN for dangerous caps
    if CapsPolicy.requires_pin(rs.manifest.caps) and ctx.caps_token != SECRET_PIN:
        return SkillOutputs(ok=False, message="PIN required for this skill capability.")
    
    try:
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

    # Subprocess mode: enhanced security with network gating
    REGISTRY.load_all()
    rs = REGISTRY.get(name)
    if not rs or not rs.enabled:
        return SkillOutputs(ok=False, message=f"Skill '{name}' not found/enabled")

    env = os.environ.copy()
    # Gate network: only allow if manifest declares 'net' capability
    if "net" not in set(rs.manifest.caps):
        env["AIDEN_NO_NET"] = "1"
    
    # Prepare payload for subprocess
    payload = {
        "name": name,
        "ctx": ctx.model_dump(),
        "args": args,
        "caps_token": caps_token
    }
    
    runner_path = os.path.join(os.path.dirname(__file__), "sandbox_runner.py")
    app_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Ensure Python path includes app root for skill imports
    env["PYTHONPATH"] = app_root + os.pathsep + env.get("PYTHONPATH", "")

    try:
        result = subprocess.run(
            [sys.executable, "-B", runner_path],
            input=json.dumps(payload).encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=TIMEOUT_SEC,
            env=env,
            cwd=app_root,
            check=False,
        )
        
        if result.returncode != 0:
            stderr_msg = result.stderr.decode()[:400]
            return SkillOutputs(ok=False, message=f"Sandbox failed rc={result.returncode}: {stderr_msg}")
        
        try:
            stdout_text = result.stdout.decode()
            if not stdout_text.strip():
                return SkillOutputs(ok=False, message="Empty output from sandbox")
            data = json.loads(stdout_text)
            return SkillOutputs(**data)
        except json.JSONDecodeError as e:
            stdout_preview = result.stdout.decode()[:200]
            stderr_preview = result.stderr.decode()[:200]
            return SkillOutputs(ok=False, message=f"Invalid JSON from sandbox: {e}. stdout: {stdout_preview}, stderr: {stderr_preview}")
            
    except subprocess.TimeoutExpired:
        return SkillOutputs(ok=False, message="Skill timed out")
    except Exception as e:
        return SkillOutputs(ok=False, message=f"Sandbox execution error: {str(e)}")