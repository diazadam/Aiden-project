"""
EAS iOS build skill - Triggers cloud builds and returns TestFlight-ready artifacts.

Features:
- Executes EAS build for iOS platform
- Supports both preview (internal) and production builds
- Extracts build URLs for monitoring and download
- Handles non-interactive builds for automation
- Returns detailed build information and status
"""
import os, json, subprocess, re
from typing import Optional
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

def _run(cmd, cwd=None, env=None, timeout=3600):
    """Run subprocess command with extended timeout for builds"""
    p = subprocess.Popen(cmd, cwd=cwd, env=env or os.environ.copy(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out, err

class Inputs(SkillInputs):
    project_dir: str
    profile: str = "preview"        # maps to eas.json profiles
    platform: str = "ios"           # ios|android
    non_interactive: bool = True
    auto_submit: bool = False       # automatically submit to App Store after build

class Outputs(SkillOutputs):
    pass

class SkillImpl(Skill):
    name = "mobile_expo_build_ios"
    version = "0.1.0"
    caps = {"exec","net","fs_write"}
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
            return Outputs(ok=False, message="EXPO_TOKEN not set in environment (required for EAS builds)")

        # Build EAS command
        cmd = ["npx", "--yes", "eas", "build", "--platform", args.platform, "--profile", args.profile]
        
        if args.non_interactive:
            cmd.append("--non-interactive")
            
        if args.auto_submit:
            cmd.append("--auto-submit")

        # Execute EAS build
        try:
            code, out, err = _run(cmd, cwd=args.project_dir, env=env, timeout=3600)
        except subprocess.TimeoutExpired:
            return Outputs(ok=False, message="EAS build timed out after 60 minutes")

        if code != 0:
            return Outputs(ok=False, message=f"EAS build failed (exit {code}): {err[:400]}")

        # Extract build information from output
        build_url = None
        build_id = None
        artifact_url = None
        
        # Look for build URLs in both stdout and stderr
        output_lines = (out.splitlines() + err.splitlines())
        
        for line in output_lines:
            # Match build dashboard URL
            if "https://expo.dev/accounts/" in line and "/builds/" in line:
                # Extract clean URL
                url_match = re.search(r'https://expo\.dev/accounts/[^/]+/projects/[^/]+/builds/[a-f0-9-]+', line)
                if url_match:
                    build_url = url_match.group(0)
                    # Extract build ID from URL
                    build_id_match = re.search(r'/builds/([a-f0-9-]+)', build_url)
                    if build_id_match:
                        build_id = build_id_match.group(1)
            
            # Match artifact download URL
            if "Build artifact:" in line or "Download URL:" in line:
                url_match = re.search(r'https://[^\s]+', line)
                if url_match:
                    artifact_url = url_match.group(0)

        # Parse additional build metadata
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

        # Determine build status
        success = code == 0
        status = "completed" if success else "failed"

        return Outputs(
            ok=success,
            message=f"EAS build {status}" + (f" - {build_url}" if build_url else ""),
            data={
                "build_url": build_url,
                "build_id": build_id,
                "artifact_url": artifact_url,
                "platform": args.platform,
                "profile": args.profile,
                "app_name": app_name,
                "bundle_identifier": bundle_id,
                "status": status,
                "exit_code": code,
                "stdout_tail": out[-800:],
                "stderr_tail": err[-400:] if err else None
            },
            artifacts={
                "build_dashboard": build_url,
                "artifact_download": artifact_url
            } if build_url else None
        )