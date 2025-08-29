"""
Subprocess skill sandbox runner with resource limits and network isolation.

This runner executes skills in a subprocess with:
- CPU time limits (30s)
- Memory limits (~800MB)
- File descriptor limits (256)
- Optional network blocking when net capability isn't granted
- Proper signal handling for clean shutdown
"""
from __future__ import annotations
import json, os, sys, time, signal, resource, importlib
from typing import Any

def _install_no_net():
    """Install network blocking by monkey-patching socket module"""
    import builtins
    import socket
    
    class _BlockedSocket(socket.socket):
        def __new__(cls, *a, **k):
            raise RuntimeError("Network disabled in sandbox")
    
    socket.socket = _BlockedSocket  # type: ignore
    socket.create_connection = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("Network disabled"))  # type: ignore

def _limit_resources():
    """Set resource limits for CPU, memory, and file descriptors"""
    # CPU time 30s
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (30, 30))
    except Exception:
        pass
    
    # Address space ~800MB
    try:
        resource.setrlimit(resource.RLIMIT_AS, (800*1024*1024, 800*1024*1024))
    except Exception:
        pass
    
    # File descriptors
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (256, 256))
    except Exception:
        pass

def main():
    """Main sandbox execution entry point"""
    payload = sys.stdin.read()
    data = json.loads(payload)
    name = data["name"]
    ctx = data["ctx"]
    args = data["args"]
    caps_token = data.get("caps_token")

    _limit_resources()

    # Respect NO_NET environment flag
    if os.environ.get("AIDEN_NO_NET") == "1":
        _install_no_net()

    # Ensure we can import skills - add current directory to path if needed
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # Import registry & run (suppress prints)
    import io
    import contextlib
    from skills.registry import REGISTRY
    from skills.contracts import SkillContext
    
    # Suppress registry loading prints
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        REGISTRY.load_all()
    
    rs = REGISTRY.get(name)
    if not rs or not rs.enabled:
        print(json.dumps({"ok": False, "message": f"skill {name} not found"}))
        return

    # PIN/caps enforcement still happens in skill runtime; here we just invoke run safely
    sctx = SkillContext(**ctx)
    try:
        inputs = rs.instance.Inputs(**args)
        out = rs.instance.run(sctx, inputs)
        print(out.model_dump_json())
    except Exception as e:
        print(json.dumps({"ok": False, "message": f"sandbox error: {str(e)[:300]}"}))

if __name__ == "__main__":
    # Kill children on SIGTERM
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    main()