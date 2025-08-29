"""
EAS iOS submission skill - Submits builds to App Store Connect for review.

Features:
- Automatically submits the latest iOS build to App Store Connect
- Supports both internal testing and App Store review submission
- Returns submission tracking URL and status
- Handles App Store Connect API authentication via EAS
- Provides submission metadata and progress tracking
"""
import os, json, subprocess, re
from typing import Optional
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

def _run(cmd, cwd=None, env=None, timeout=1800):  # 30 min timeout for submission
    """Run subprocess command with extended timeout for App Store submission"""
    p = subprocess.Popen(cmd, cwd=cwd, env=env or os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out, err

class Inputs(SkillInputs):
    project_dir: str
    platform: str = "ios"
    latest: bool = True              # submit latest build
    non_interactive: bool = True
    app_store: bool = True          # submit to App Store (vs internal testing)

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "mobile_expo_submit_ios"
    version = "0.1.0"
    caps = {"exec","net"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        # Verify project directory exists
        if not os.path.exists(args.project_dir):
            return Outputs(ok=False, message=f"Project directory not found: {args.project_dir}")
        
        # Verify Expo project structure
        if not os.path.exists(os.path.join(args.project_dir, "app.json")):
            return Outputs(ok=False, message="Not a valid Expo project - app.json missing")

        # Check for required environment variables
        env = os.environ.copy()
        if "EXPO_TOKEN" not in env:
            return Outputs(ok=False, message="EXPO_TOKEN not set in environment (required for EAS submission)")

        # Build EAS submit command
        cmd = ["npx", "--yes", "eas", "submit", "--platform", args.platform]
        
        if args.latest:
            cmd.append("--latest")
            
        if args.non_interactive:
            cmd.append("--non-interactive")

        # Execute EAS submit
        try:
            code, out, err = _run(cmd, cwd=args.project_dir, env=env, timeout=1800)
        except subprocess.TimeoutExpired:
            return Outputs(ok=False, message="EAS submission timed out after 30 minutes")

        if code != 0:
            return Outputs(ok=False, message=f"EAS submission failed (exit {code}): {err[:400]}")

        # Extract submission information from output
        submission_url = None
        submission_id = None
        app_store_state = None
        
        # Look for submission details in both stdout and stderr
        output_lines = (out.splitlines() + err.splitlines())
        
        for line in output_lines:
            # Match App Store Connect submission URL
            if "https://appstoreconnect.apple.com" in line:
                url_match = re.search(r'https://appstoreconnect\.apple\.com[^\s]+', line)
                if url_match:
                    submission_url = url_match.group(0)
            
            # Match submission ID
            if "Submission ID:" in line or "submission" in line.lower() and "id" in line.lower():
                id_match = re.search(r'[a-f0-9-]{36}|[a-f0-9]{32}', line)
                if id_match:
                    submission_id = id_match.group(0)
            
            # Match App Store status
            if "status" in line.lower() and ("pending" in line.lower() or "processing" in line.lower() or "ready" in line.lower()):
                app_store_state = line.strip()

        # Parse app metadata
        app_name = None
        bundle_id = None
        try:
            app_json_path = os.path.join(args.project_dir, "app.json")
            with open(app_json_path, 'r') as f:
                app_config = json.load(f)
                expo_config = app_config.get("expo", {})
                app_name = expo_config.get("name")
                ios_config = expo_config.get("ios", {})
                bundle_id = ios_config.get("bundleIdentifier")
        except Exception:
            pass

        # Determine submission status
        success = code == 0
        status = "submitted" if success else "failed"

        return Outputs(
            ok=success,
            message=f"App Store submission {status}" + (f" - {submission_url}" if submission_url else ""),
            data={
                "submission_url": submission_url,
                "submission_id": submission_id,
                "app_store_state": app_store_state,
                "platform": args.platform,
                "app_name": app_name,
                "bundle_identifier": bundle_id,
                "status": status,
                "exit_code": code,
                "stdout_tail": out[-800:],
                "stderr_tail": err[-400:] if err else None
            },
            artifacts={
                "app_store_connect": submission_url
            } if submission_url else None
        )