#!/usr/bin/env python3
import os, sys

if len(sys.argv) < 2:
    print("Usage: verify_power_stack.py /absolute/path/to/Aiden-project")
    sys.exit(1)

root = sys.argv[1]
app = os.path.join(root, "apps", "replit-mvp")
checks = [
  "brain/capability_manifest.py",
  "brain/toolcards.yaml",
  "brain/toolcards.py",
  "brain/memory_supabase.py",
  "brain/power_planner.py",
  "connectors/n8n.py",
  "telemetry/ledger.py",
  "public/control-tower.html",
  "skills/_system/bigquery_query/manifest.json",
  "skills/_system/bigquery_query/skill.py",
  "skills/_system/gcs_upload/manifest.json",
  "skills/_system/gcs_upload/skill.py",
  "skills/_system/cloud_run_deploy/manifest.json",
  "skills/_system/cloud_run_deploy/skill.py",
  "requirements.txt",
  "main.py",
]
missing = [rel for rel in checks if not os.path.exists(os.path.join(app, rel))]
if missing:
    print("❌ Missing:", *missing, sep="\n - ")
    sys.exit(2)
print("✅ Power stack looks good at", app)