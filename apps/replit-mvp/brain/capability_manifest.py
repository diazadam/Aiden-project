"""
AIDEN CAPABILITY MANIFEST - Real-time awareness of available resources
"""
from __future__ import annotations
import os

def build_capability_manifest() -> dict:
    gcp_project = os.environ.get("GCP_PROJECT_ID", "<unset>")
    manifest = {
        "gcp_project": gcp_project,
        "enabled_apis_hint": [
            "bigquery.googleapis.com","run.googleapis.com","storage.googleapis.com",
            "pubsub.googleapis.com","secretmanager.googleapis.com","aiplatform.googleapis.com"
        ],
        "connectors": {
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "gcp_sa": bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")),
            "supabase": bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY")),
            "n8n": bool(os.environ.get("N8N_WEBHOOK_BASE")),
        },
    }

    manifest["power_statement"] = f"""
You are AidenAI, an execution-first agent with access to:
- Google Cloud (project: {gcp_project}): BigQuery (analytics), Cloud Storage (artifacts), Cloud Run (deployments),
  Pub/Sub (pipelines), Secret Manager (secrets), Vertex AI (genAI/ML).
- OpenAI: GPT-4o (planning, function-calling), embeddings, vision.
- Supabase: Postgres + Storage + (optional) pgvector for long-term memory and artifacts.
- n8n: Workflow automation via webhooks for 350+ integrations.
- Local skills: Browser/Playwright, Image tools, Mobile (Expo/EAS), Website generator, and a growing skill registry.
ALWAYS map goals to these tools, execute end-to-end, and save outcomes to Supabase/Cloud Storage.
Return a concrete plan, the tool calls you will make, and links to produced artifacts.
"""
    return manifest

def _get_available_skills() -> list:
    """Get currently available skills from registry"""
    try:
        from skills.registry import REGISTRY
        return [skill['name'] for skill in REGISTRY.list()]
    except Exception:
        # Fallback list of expected skills
        return [
            "web_fetch",
            "bigquery_safe", 
            "gcs_upload",
            "cloud_run_deploy",
            "mobile_expo_scaffold",
            "mobile_expo_build_ios",
            "mobile_expo_submit_ios",
            "browser"
        ]