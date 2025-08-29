"""
Subprocess skill validation system - Isolated testing environment for proposed skills
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
import tempfile
import json
import venv
import hashlib
import textwrap
from typing import Tuple

from .registry import PENDING_DIR
SKILLS_PACKAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
APP_ROOT = os.path.abspath(os.path.join(SKILLS_PACKAGE_DIR, ".."))

def _run(cmd: list[str], env: dict, cwd: str | None = None, timeout: int = 120) -> Tuple[int, str, str]:
    """Run a command with timeout and capture output"""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd, env=env, text=True)
    try:
        out, err = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        out, err = p.communicate()
        return (124, out, "TIMEOUT\n"+err)
    return (p.returncode, out, err)

def validate_pending_skill(name: str) -> dict:
    """
    Validate a pending skill in an isolated subprocess environment
    
    Process:
    1. Create disposable venv
    2. Install test dependencies
    3. Set up sandboxed package structure
    4. Run import smoke test
    5. Run pytest if tests exist
    6. Return structured results
    """
    pending = os.path.join(PENDING_DIR, name)
    if not os.path.isdir(pending):
        return {"ok": False, "message": "pending skill not found"}

    # Build a disposable venv
    vroot = os.path.join("/tmp/aiden_validate", name)
    if os.path.exists(vroot):
        shutil.rmtree(vroot)
    os.makedirs(vroot, exist_ok=True)
    venv_dir = os.path.join(vroot, "venv")
    venv.EnvBuilder(with_pip=True).create(venv_dir)

    py = os.path.join(venv_dir, "bin", "python")
    pip = os.path.join(venv_dir, "bin", "pip")

    # Install minimal deps for tests
    reqs = ["pytest"]
    tests_reqs = os.path.join(pending, "tests", "requirements.txt")
    if os.path.exists(tests_reqs):
        reqs.append(f"-r{tests_reqs}")

    code = 0
    out = ""
    err = ""

    # Install requirements
    code, out, err = _run([pip, "install", *reqs], env=os.environ.copy(), cwd=None, timeout=240)
    if code != 0:
        return {"ok": False, "message": "pip install failed", "stderr": err[:1000]}

    # Create a sandboxed package path so '..contracts' resolves:
    # We copy pending skill into skills/_sandboxed/<name> to mirror package layout.
    sandbox_pkg = os.path.join(SKILLS_PACKAGE_DIR, "_sandboxed", name)
    if os.path.exists(sandbox_pkg):
        shutil.rmtree(sandbox_pkg)
    os.makedirs(sandbox_pkg, exist_ok=True)
    
    # Copy skill.py and manifest.json
    for fn in ["skill.py", "manifest.json"]:
        src = os.path.join(pending, fn)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(sandbox_pkg, fn))

    # Smoke import: try importing "skills._sandboxed.<name>.skill"
    env = os.environ.copy()
    env["PYTHONPATH"] = APP_ROOT + os.pathsep + env.get("PYTHONPATH", "")

    smoke = textwrap.dedent(f"""
    import importlib
    mod = importlib.import_module("skills._sandboxed.{name}.skill")
    assert hasattr(mod, "SkillImpl"), "SkillImpl not found"
    print("Import smoke test passed")
    """).strip()

    code, out, err = _run([py, "-c", smoke], env=env, cwd=APP_ROOT, timeout=60)
    if code != 0:
        return {"ok": False, "message": "import smoke test failed", "stderr": err[:1000]}

    # If tests exist, run them
    tests_dir = os.path.join(pending, "tests")
    test_result = {"ran_tests": False, "exit_code": 0, "stdout": "", "stderr": ""}
    if os.path.isdir(tests_dir):
        # Copy tests to sandboxed location
        sandbox_tests = os.path.join(sandbox_pkg, "tests")
        shutil.copytree(tests_dir, sandbox_tests)
        
        code, tout, terr = _run([py, "-m", "pytest", "-q", sandbox_tests], env=env, cwd=APP_ROOT, timeout=240)
        test_result = {"ran_tests": True, "exit_code": code, "stdout": tout[-1000:], "stderr": terr[-1000:]}
        if code != 0:
            return {"ok": False, "message": "pytest failed", "result": test_result}

    # Clean up sandboxed files
    if os.path.exists(sandbox_pkg):
        shutil.rmtree(sandbox_pkg)

    return {"ok": True, "message": "validation passed", "result": test_result}