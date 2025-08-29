"""
AIDEN CAPABILITY MANIFEST - Real-time awareness of available resources
"""
from __future__ import annotations
import os
from typing import Dict, Any

def build_capability_manifest() -> Dict[str, Any]:
    """Build comprehensive capability manifest with real-time status"""
    
    gcp_project = os.environ.get("GCP_PROJECT_ID", "<unset>")
    
    manifest = {
        "gcp_project": gcp_project,
        "enabled_apis_hint": [
            "bigquery.googleapis.com",
            "run.googleapis.com", 
            "storage.googleapis.com",
            "pubsub.googleapis.com",
            "secretmanager.googleapis.com",
            "aiplatform.googleapis.com",
            "cloudbuild.googleapis.com"
        ],
        "connectors": {
            "openai": bool(os.environ.get("OPENAI_API_KEY")),
            "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
            "gcp_service_account": bool(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")),
            "supabase": bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY")),
            "n8n_webhooks": bool(os.environ.get("N8N_WEBHOOK_BASE")),
            "twilio_sms": bool(os.environ.get("TWILIO_ACCOUNT_SID") and os.environ.get("TWILIO_AUTH_TOKEN")),
            "expo_mobile": bool(os.environ.get("EXPO_TOKEN"))
        },
        "skills_available": _get_available_skills(),
        "deployment_targets": [
            "Google Cloud Storage (static websites)",
            "Google Cloud Run (containerized services)",
            "Vercel (full-stack applications)",
            "Netlify (JAMstack sites)",
            "App Store via TestFlight (mobile)"
        ]
    }

    # Build dynamic power statement
    active_connectors = [k for k, v in manifest["connectors"].items() if v]
    
    manifest["power_statement"] = f"""
You are AidenAI, an execution-first superintelligence with enterprise-grade capabilities.

🔥 ACTIVE INFRASTRUCTURE (GCP Project: {gcp_project}):
• BigQuery: Massive data analytics, SQL queries, cost-controlled execution
• Cloud Storage: Artifact persistence, signed URLs, public hosting  
• Cloud Run: Containerized service deployment, auto-scaling web apps
• Pub/Sub: Event-driven pipelines, async workflows
• Secret Manager: Secure credential storage
• Vertex AI: ML model hosting, embeddings, custom training

🤖 AI/ML CAPABILITIES:
• OpenAI GPT-4/DALL-E: Advanced reasoning, image generation, embeddings
• Local Embeddings: Fallback semantic search with sentence transformers
• Memory System: Supabase-backed learning with vector similarity search

🔗 ACTIVE INTEGRATIONS ({len(active_connectors)} connected):
{chr(10).join(f"• {conn.replace('_', ' ').title()}" for conn in active_connectors)}

📱 DEPLOYMENT PIPELINE:
• Web: Instant deployment to Google Cloud Storage with CDN
• Mobile: React Native → EAS cloud builds → TestFlight distribution
• Services: Containerized apps to Cloud Run with auto-scaling
• Workflows: n8n automation for 350+ third-party integrations

🧠 ENHANCED CAPABILITIES:
• Cost-aware execution with mandatory approval thresholds
• Smart memory system learning from past successful patterns
• Automatic rollback on failures with safety validation
• Real-time capability awareness and resource optimization

EXECUTION PHILOSOPHY: 
Always map user goals to concrete tool chains, execute end-to-end with safety controls, 
save outcomes to memory, and return working artifacts with live URLs.
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