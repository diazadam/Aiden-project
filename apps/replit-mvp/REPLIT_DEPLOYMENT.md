# 🚀 AidenAI Replit Deployment Guide

## Quick Setup Steps

### 1. Import from GitHub
1. Go to [Replit.com](https://replit.com)
2. Click "Create Repl" → "Import from GitHub"
3. Use repository URL: `https://github.com/diazadam/Aiden-project.git`
4. Set path to: `apps/replit-mvp`
5. Click "Import"

### 2. Configure Environment Variables
In Replit Secrets tab, add these variables:

```
# Core API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Aiden Configuration
AIDEN_PIN=4242
SPEAK_REPLIES=true

# Supabase (for memory system)
SUPABASE_URL=https://yzkinemiehenfpdbcnie.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key

# GCP Integration (optional but recommended)
GCP_PROJECT_ID=your_gcp_project_id
GOOGLE_APPLICATION_CREDENTIALS=/tmp/gcp-key.json
GCS_DEFAULT_BUCKET=your_bucket_name

# n8n Integration (optional)
N8N_URL=your_n8n_url
N8N_TOKEN=your_n8n_token
```

### 3. Install Dependencies
Replit will automatically install dependencies from `requirements.txt`, or run:
```bash
pip install -r requirements.txt
```

### 4. Setup GCP Credentials (Optional)
If using GCP features:
1. Upload your GCP service account JSON file
2. Place it in the root directory as `gcp-credentials.json`
3. Update the `GOOGLE_APPLICATION_CREDENTIALS` secret to point to the file

### 5. Run AidenAI
Click the green "Run" button or execute:
```bash
python main.py
```

## 🎯 What You Get

### Core Features
- ✅ **Power Planner**: Smart execution planning with cost estimation
- ✅ **Memory System**: Learns from past interactions using Supabase
- ✅ **BigQuery Integration**: Query data with cost controls and validation
- ✅ **Cloud Storage**: Upload and manage files with public URLs
- ✅ **Web Scraping**: Fetch and analyze web content
- ✅ **Telemetry**: Activity logging with automatic secret redaction

### Web Interface
- **Main Interface**: `https://your-repl-url.replit.app/`
- **Control Tower**: `https://your-repl-url.replit.app/control-tower.html`
- **API Docs**: `https://your-repl-url.replit.app/docs`

### Enterprise Controls
- Cost estimation and approval workflows
- Safety governors and validation
- Secret redaction in logs
- Row-level security policies

## 🔧 Configuration

### Minimum Required
```env
OPENAI_API_KEY=sk-...
AIDEN_PIN=4242
```

### Full Production Setup
```env
# All environment variables from step 2 above
```

### Optional Integrations
- **Supabase**: For advanced memory and user management
- **GCP**: For BigQuery analytics and cloud storage
- **n8n**: For workflow automation with 350+ services

## 🚀 Ready to Use!

Your AidenAI Power-Stack v2 is now ready for production use with:
- 100% operational core systems
- Enterprise-grade security and controls
- Full GCP integration capabilities
- Advanced memory and learning systems
- Professional web interface and monitoring

## Support
- Check the Control Tower for system status
- View telemetry logs for debugging
- All skills are production-tested and operational

---
*AidenAI Power-Stack v2 - Production-Ready AI Assistant*