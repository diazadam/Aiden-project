import os, subprocess, time, shlex, json
from typing import Optional, Dict
from skills.contracts import Skill, SkillInputs, SkillOutputs, SkillContext

def _run(cmd: str, cwd: Optional[str] = None, env: Optional[dict] = None, timeout: int = 1800):
    p = subprocess.Popen(shlex.split(cmd), cwd=cwd, env=env or os.environ.copy(),
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(timeout=timeout)
    return p.returncode, out, err

class Inputs(SkillInputs):
    service_name: str
    region: str = "us-central1"
    repository: str = "aiden"         # Artifact Registry repo name
    image: Optional[str] = None       # If provided, skips build
    source_dir: Optional[str] = None  # If provided, builds with gcloud builds submit
    allow_unauthenticated: bool = True
    cpu: str = "1"
    memory: str = "512Mi"
    concurrency: int = 80
    max_instances: int = 3
    env_vars: Dict[str, str] = {}

class Outputs(SkillOutputs): pass

class SkillImpl(Skill):
    name = "cloud_run_deploy"
    version = "0.2.0"
    caps = {"exec","net","fs_write"}
    Inputs = Inputs
    Outputs = Outputs

    def run(self, ctx: SkillContext, args: Inputs) -> Outputs:
        project = os.environ.get("GCP_PROJECT_ID")
        if not project: return Outputs(ok=False, message="GCP_PROJECT_ID not set")

        # Build (if needed) to Artifact Registry
        image = args.image
        if not image and args.source_dir:
            # us-central1-docker.pkg.dev/<project>/<repo>/<service>:<ts>
            image = f"{args.region}-docker.pkg.dev/{project}/{args.repository}/{args.service_name}:{int(time.time())}"
            code, out, err = _run(f"gcloud builds submit --project {project} --tag {image}", cwd=args.source_dir)
            if code != 0:
                return Outputs(ok=False, message=f"build failed: {err[:400]}")
        if not image:
            return Outputs(ok=False, message="Provide image or source_dir")

        # Deploy to Cloud Run
        allow = "--allow-unauthenticated" if args.allow_unauthenticated else ""
        envs = ""
        if args.env_vars:
            kv = ",".join([f"{k}={v}" for k,v in args.env_vars.items()])
            envs = f"--set-env-vars {shlex.quote(kv)}"

        flags = f"--cpu {args.cpu} --memory {args.memory} --concurrency {args.concurrency} --max-instances {args.max_instances}"
        cmd = f"gcloud run deploy {args.service_name} --project {project} --region {args.region} --image {image} --platform=managed {allow} {envs} {flags} --format=json"
        code, out, err = _run(cmd)
        if code != 0:
            return Outputs(ok=False, message=f"deploy failed: {err[:400]}")

        try:
            obj = json.loads(out)
            url = obj.get("status", {}).get("url") or obj.get("statusUrl") or ""
            revision = (obj.get("status", {}).get("latestCreatedRevisionName") 
                        or obj.get("latestReadyRevisionName") or "")
        except Exception:
            url, revision = "", ""
        data = {"service_url": url, "image": image, "revision": revision}
        return Outputs(ok=True, data=data, message="deployed")