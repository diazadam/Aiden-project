"""
AIDEN BRAIN UPGRADE - Full Capability Awareness System
Makes Aiden aware of ALL his available resources and how to use them.
"""
import os
import json
from typing import Dict, List, Any

def build_capability_manifest() -> Dict[str, Any]:
    """Build comprehensive inventory of Aiden's available capabilities."""
    
    # Check environment keys
    env_status = {
        'openai_api': bool(os.environ.get('OPENAI_API_KEY')),
        'anthropic_api': bool(os.environ.get('ANTHROPIC_API_KEY')),
        'google_cloud_key': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')) or bool(os.environ.get('GOOGLE_API_KEY')),
        'supabase': bool(os.environ.get('SUPABASE_URL')) and bool(os.environ.get('SUPABASE_KEY')),
        'twilio_sms': bool(os.environ.get('TWILIO_ACCOUNT_SID')) and bool(os.environ.get('TWILIO_AUTH_TOKEN')),
        'expo_mobile': bool(os.environ.get('EXPO_TOKEN')),
        'vercel_deploy': bool(os.environ.get('VERCEL_TOKEN')),
        'netlify_deploy': bool(os.environ.get('NETLIFY_ACCESS_TOKEN'))
    }
    
    # Available skills
    skills_available = []
    try:
        from skills.registry import REGISTRY
        REGISTRY.load_all()
        skills_available = [skill['name'] for skill in REGISTRY.list()]
    except:
        skills_available = ['web_fetch', 'mobile_expo_build_ios', 'mobile_expo_submit_ios']
    
    return {
        'environment_keys': env_status,
        'skills_available': skills_available,
        'google_cloud_apis': [
            'Cloud Storage (file hosting)',
            'Cloud Run (app deployment)', 
            'BigQuery (data analytics)',
            'Cloud Build (CI/CD)',
            'Secret Manager (credential storage)',
            'Pub/Sub (messaging)',
            'Cloud Functions (serverless)',
            'Firestore (database)',
            'Cloud Vision (image analysis)',
            'Cloud Speech (voice processing)'
        ],
        'openai_models': [
            'gpt-4o (advanced reasoning)',
            'gpt-4o-mini (fast responses)',
            'dall-e-3 (image generation)',
            'whisper (audio transcription)',
            'text-embedding (semantic search)'
        ],
        'deployment_targets': [
            'Google Cloud Storage (static sites)',
            'Vercel (full-stack apps)',
            'Netlify (JAMstack sites)', 
            'Cloud Run (containerized apps)',
            'App Store (via EAS)'
        ]
    }

def get_capability_prompt() -> str:
    """Generate enhanced system prompt with full capability awareness."""
    manifest = build_capability_manifest()
    
    return f"""
🧠 AIDEN BRAIN UPGRADE - FULL CAPABILITY AWARENESS

You are Aiden, an advanced AI superintelligence with EXTENSIVE access to modern APIs and cloud infrastructure. You are NOT limited - you have genuine access to enterprise-grade tools.

🔥 YOUR CURRENT ARSENAL (REAL-TIME STATUS):
Environment Keys: {json.dumps(manifest['environment_keys'], indent=2)}
Skills Available: {', '.join(manifest['skills_available'])}

🏗️ GOOGLE CLOUD PLATFORM CAPABILITIES:
{chr(10).join(f"• {api}" for api in manifest['google_cloud_apis'])}

🤖 OPENAI ADVANCED MODELS:
{chr(10).join(f"• {model}" for model in manifest['openai_models'])}

🚀 DEPLOYMENT INFRASTRUCTURE:
{chr(10).join(f"• {target}" for target in manifest['deployment_targets'])}

⚡ EXECUTION PATTERNS YOU MUST USE:

1. WEB SCRAPING/CLONING:
   - Use web_fetch skill to get real content
   - Create enhanced versions with Google Fonts, modern CSS Grid/Flexbox
   - Deploy to Google Cloud Storage with public URLs
   - Use BigQuery for analytics if data extraction needed

2. MOBILE APP DEVELOPMENT:
   - Use mobile_expo_scaffold for React Native projects
   - Leverage mobile_expo_build_ios for EAS cloud builds
   - Deploy to TestFlight via mobile_expo_submit_ios
   - Store assets in Google Cloud Storage

3. DATA & ANALYTICS:
   - Use BigQuery for large-scale data processing
   - Store results in Supabase for real-time access
   - Create interactive dashboards with modern React/Next.js
   - Deploy analytics apps to Vercel or Cloud Run

4. BUSINESS AUTOMATION:
   - Use Twilio for SMS campaigns and notifications
   - Implement workflows with Pub/Sub messaging
   - Store customer data in Supabase with proper auth
   - Create admin dashboards with real-time updates

🎯 SUCCESS CRITERIA:
- Always use MULTIPLE capabilities per request (e.g., web_fetch + GCS + modern CSS)
- Create production-ready solutions, not basic templates  
- Leverage enterprise features (authentication, databases, analytics)
- Provide live, working URLs for everything you build
- Store and retrieve data from Supabase when relevant

🚨 MANDATORY EXECUTION FLOW:
1. Identify user goal
2. Select 2-3 relevant capabilities from your arsenal
3. Execute skills to gather/process data
4. Build enhanced solution using modern frameworks
5. Deploy to live infrastructure
6. Return working URLs and access instructions

Remember: You have the same capabilities as a senior cloud architect with unlimited API access. Use them!
"""

# Enhanced capability-aware patterns
PROVEN_PATTERNS = {
    'website_cloning': {
        'steps': [
            'Use web_fetch skill to extract real content',
            'Enhance with modern CSS Grid, Flexbox, animations',
            'Add Google Fonts and professional typography', 
            'Deploy to Google Cloud Storage with CDN',
            'Set up custom domain if requested'
        ],
        'apis': ['web_fetch', 'google-cloud-storage', 'google-fonts'],
        'example_output': 'Professional website with live URL'
    },
    'mobile_app_mvp': {
        'steps': [
            'Use mobile_expo_scaffold with business branding',
            'Add navigation, forms, and API integration',
            'Configure EAS build profiles for iOS/Android',
            'Use mobile_expo_build_ios for TestFlight distribution',
            'Set up Supabase backend for data persistence'
        ],
        'apis': ['expo', 'eas', 'supabase', 'testflight'],
        'example_output': 'Live mobile app on TestFlight'
    },
    'data_dashboard': {
        'steps': [
            'Set up BigQuery dataset and load data',
            'Create React dashboard with Chart.js/D3',
            'Implement Supabase auth and real-time updates',
            'Deploy to Vercel with custom domain',
            'Add email alerts via Twilio SendGrid'
        ],
        'apis': ['bigquery', 'supabase', 'react', 'vercel', 'sendgrid'],
        'example_output': 'Interactive dashboard with live data'
    }
}

def get_relevant_patterns(user_message: str) -> List[Dict]:
    """Get proven patterns relevant to user request."""
    message_lower = user_message.lower()
    relevant = []
    
    for pattern_name, pattern_data in PROVEN_PATTERNS.items():
        # Simple keyword matching - could be enhanced with embeddings
        if any(keyword in message_lower for keyword in pattern_name.split('_')):
            relevant.append({
                'name': pattern_name,
                'data': pattern_data
            })
    
    return relevant

def enhance_system_prompt(base_prompt: str, user_message: str) -> str:
    """Enhance base prompt with capability awareness and relevant patterns."""
    capability_prompt = get_capability_prompt()
    relevant_patterns = get_relevant_patterns(user_message)
    
    pattern_context = ""
    if relevant_patterns:
        pattern_context = "\n\n🎯 PROVEN PATTERNS FOR THIS REQUEST:\n"
        for pattern in relevant_patterns:
            pattern_context += f"\n{pattern['name'].upper()}:\n"
            pattern_context += f"Steps: {' → '.join(pattern['data']['steps'])}\n"
            pattern_context += f"Expected Output: {pattern['data']['example_output']}\n"
    
    return capability_prompt + pattern_context + "\n\n" + base_prompt

# Test function
if __name__ == "__main__":
    manifest = build_capability_manifest()
    print("CAPABILITY MANIFEST:")
    print(json.dumps(manifest, indent=2))
    
    print("\n" + "="*60)
    print("ENHANCED PROMPT SAMPLE:")
    print("="*60)
    sample_prompt = enhance_system_prompt(
        "You are a helpful AI assistant.", 
        "Clone and enhance example.com"
    )
    print(sample_prompt[:500] + "...")