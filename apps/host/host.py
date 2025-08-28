#!/usr/bin/env python3
"""
Local Host Bridge — PIN-protected executor for allowlisted commands

Usage:
  python host.py list                           # Show available commands
  python host.py run "command" key=value       # Execute with parameters  
  python host.py run "command" --dry-run       # Show what would run
"""
import os, subprocess, sys, datetime
from pathlib import Path
from getpass import getpass
from dotenv import load_dotenv
import yaml

ROOT = Path(__file__).resolve().parents[2]  # project root
load_dotenv(ROOT/".env.local")

PIN = os.getenv("AIDEN_PIN", "2188")
ALLOWLIST_PATH = Path(__file__).resolve().parent / "allowlist.yaml"
LOG_PATH = ROOT / "logs" / "host_executor.log"


def log_execution(command_name: str, template: str, params: dict, result: int):
    """Log command execution for audit trail"""
    LOG_PATH.parent.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"{timestamp} | {command_name} | params={params} | exit={result}\n"
    with LOG_PATH.open("a") as f:
        f.write(log_entry)


def load_allowlist():
    """Load and return the allowlist commands"""
    if not ALLOWLIST_PATH.exists():
        return {}
    try:
        data = yaml.safe_load(ALLOWLIST_PATH.read_text())
        return data or {}
    except Exception as e:
        print(f"ERROR: Failed to load allowlist: {e}", file=sys.stderr)
        return {}


def format_cmd(template: str, params: dict) -> str:
    """Format command template with parameters"""
    try:
        cmd = template.format(**params)
    except KeyError as e:
        missing = e.args[0]
        raise ValueError(f"Missing required parameter: {missing}")
    return os.path.expanduser(cmd)


def validate_pin():
    """Validate PIN with fallback to prompt"""
    provided = os.getenv("CLI_PIN")
    if not provided:
        provided = getpass("🔒 Host Executor PIN: ").strip()
    
    if provided != PIN:
        raise PermissionError("Invalid PIN - access denied")
    return True


def run_allowed(name: str, params: dict, dry_run: bool = False):
    """Execute an allowlisted command with PIN protection"""
    allowlist = load_allowlist()
    
    if not allowlist:
        raise ValueError("No allowlist found - check allowlist.yaml")
    
    if name not in allowlist:
        available = list(allowlist.keys())
        raise ValueError(f"Command '{name}' not allowed. Available: {', '.join(available)}")
    
    template = allowlist[name]
    
    try:
        cmd = format_cmd(template, params)
    except ValueError as e:
        print(f"Parameter error: {e}", file=sys.stderr)
        print(f"Template: {template}", file=sys.stderr)
        return 1
    
    if dry_run:
        print(f"[DRY RUN] Would execute: {cmd}")
        return 0
    
    # PIN gate for actual execution
    validate_pin()
    
    print(f"🔄 Executing: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Log the execution
        log_execution(name, template, params, result.returncode)
        
        # Show output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        if result.returncode != 0:
            print(f"⚠️  Command exited with code {result.returncode}", file=sys.stderr)
            
        return result.returncode
        
    except Exception as e:
        print(f"Execution error: {e}", file=sys.stderr)
        log_execution(name, template, params, -1)
        return 1


def list_commands():
    """List all available commands"""
    allowlist = load_allowlist()
    if not allowlist:
        print("No commands available - check allowlist.yaml")
        return
        
    print("📋 Available Commands:")
    print("-" * 50)
    for name, template in allowlist.items():
        print(f"• {name:<15} → {template}")
    print(f"\n🔧 Total: {len(allowlist)} commands")


def main(argv):
    import argparse
    
    ap = argparse.ArgumentParser(
        description="Local Host Bridge — PIN-protected executor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python host.py list
  python host.py run "open cursor" path="/Users/adam/project" 
  python host.py run "git clone" repo="https://github.com/owner/repo" dest="~/repos/repo"
  python host.py run "npm dev" path="~/my-app" --dry-run
        """
    )
    
    ap.add_argument("action", choices=["list", "run"], help="Action to perform")
    ap.add_argument("name", nargs="?", help="Command name to run")
    ap.add_argument("params", nargs="*", help="Parameters as key=value pairs")
    ap.add_argument("--dry-run", action="store_true", help="Show command without executing")
    
    args = ap.parse_args(argv)
    
    if args.action == "list":
        list_commands()
        return 0
    
    if args.action == "run":
        if not args.name:
            print("ERROR: Command name required for 'run' action", file=sys.stderr)
            return 1
            
        # Parse key=value parameters
        params = {}
        for param in args.params:
            if "=" not in param:
                print(f"WARNING: Ignoring invalid parameter '{param}' (expected key=value)", file=sys.stderr)
                continue
            key, value = param.split("=", 1)
            params[key.strip()] = value.strip()
        
        try:
            return run_allowed(args.name, params, args.dry_run)
        except (ValueError, PermissionError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))