import os, io, json, zipfile, fnmatch
from typing import Optional, Literal, List, Dict, Any
from pathlib import Path
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Import superintelligence
from superintelligence import AIDEN_SUPERINTELLIGENCE

# ---- Setup & Config ----
ROOT = Path(__file__).parent
PROJECT_ROOT = ROOT.parent.parent
load_dotenv(PROJECT_ROOT/".env.local", override=False)

APP_NAME    = os.getenv("APP_NAME", "Aiden Control Tower")
PROVIDER    = os.getenv("PROVIDER", "openai").lower()  # openai|anthropic
OPENAI_KEY  = os.getenv("OPENAI_API_KEY")
ANTH_KEY    = os.getenv("ANTHROPIC_API_KEY")
N8N_URL     = os.getenv("N8N_URL")
N8N_TOKEN   = os.getenv("N8N_TOKEN")
DISPATCH_PIN= os.getenv("DISPATCH_PIN") or os.getenv("AIDEN_PIN", "4242")

# ---- Memory Helpers ----
SB_URL = (os.getenv("SUPABASE_URL") or "").rstrip("/")
SB_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_JWT") or ""

async def sb_upsert_message(account_id:str, role:str, text:str, thread_id:str|None=None, trace_id:str|None=None):
    """Store conversation in Supabase users table as JSON in full_name field"""
    if not (SB_URL and SB_KEY): return None
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            # Check if user exists
            r = await c.get(f"{SB_URL}/rest/v1/users?email=eq.{account_id}@aiden.local",
                headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"})
            
            if r.status_code == 200 and r.json():
                # User exists, update conversation history
                user = r.json()[0]
                current_history = user.get("full_name", "[]")
                try:
                    history = json.loads(current_history) if current_history != "[]" else []
                except:
                    history = []
                
                # Add new message
                history.append({
                    "role": role,
                    "content": text,
                    "timestamp": str(datetime.now()),
                    "trace_id": trace_id
                })
                
                # Keep only last 20 messages
                history = history[-20:]
                
                # Update user
                await c.patch(f"{SB_URL}/rest/v1/users?email=eq.{account_id}@aiden.local",
                    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"},
                    json={"full_name": json.dumps(history)})
            else:
                # Create new user with conversation history
                history = [{
                    "role": role,
                    "content": text,
                    "timestamp": str(datetime.now()),
                    "trace_id": trace_id
                }]
                
                await c.post(f"{SB_URL}/rest/v1/users",
                    headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}","Content-Type":"application/json"},
                    json={
                        "email": f"{account_id}@aiden.local",
                        "full_name": json.dumps(history),
                        "subscription_tier": "aiden_user"
                    })
    except Exception as e:
        print(f"Memory error: {e}")
    return account_id

async def sb_recent_messages(account_id:str, limit:int=20):
    """Retrieve conversation history from Supabase users table"""
    if not (SB_URL and SB_KEY): return []
    try:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(f"{SB_URL}/rest/v1/users?email=eq.{account_id}@aiden.local",
                headers={"apikey":SB_KEY,"Authorization":f"Bearer {SB_KEY}"})
            
            if r.status_code == 200 and r.json():
                user = r.json()[0]
                history_str = user.get("full_name", "[]")
                try:
                    history = json.loads(history_str) if history_str != "[]" else []
                    # Return last N messages in the format expected by the LLM
                    recent = history[-limit:] if len(history) > limit else history
                    return [{"role": msg["role"], "content": msg["content"]} for msg in recent]
                except:
                    return []
            return []
    except Exception as e:
        print(f"Memory retrieval error: {e}")
        return []

app = FastAPI(title=APP_NAME)

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ---- Models ----
class Customer(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None

class TaskParams(BaseModel):
    # free-form; common fields listed for docs
    customer: Optional[Customer] = None
    to: Optional[str] = None
    body: Optional[str] = None
    service: Optional[str] = None
    zip: Optional[str] = None
    window: Optional[str] = None
    notes: Optional[str] = None

class TaskCard(BaseModel):
    trace_id: Optional[str] = None
    account_id: Optional[str] = None
    type: Literal[
        "send_sms",
        "book_appointment", 
        "update_crm",
        "ingest_knowledge",
        "repo_install",
        "deploy",
        "report_daily"
    ]
    source: Optional[str] = "dashboard"
    params: TaskParams = Field(default_factory=TaskParams)
    meta: Optional[dict] = None
    approval: Optional[dict] = None

class ChatIn(BaseModel):
    message: str
    account_id: Optional[str] = None
    business_name: Optional[str] = None
    industry: Optional[str] = None

class ChatOut(BaseModel):
    assistant: str
    taskcard: Optional[TaskCard] = None

# ---- LLM helpers ----
SYSTEM = (
    "You are Aiden, an expert AI business automation consultant. You help users build million-dollar automation systems.\n\n"
    
    "COMMUNICATION STYLE:\n"
    "- Be enthusiastic and encouraging about automation opportunities\n"
    "- Use business language and focus on ROI, efficiency, and growth\n"
    "- Provide specific, actionable recommendations\n"
    "- Ask intelligent follow-up questions to understand business needs\n\n"
    
    "RESPONSE FORMAT:\n"
    "Always return JSON with 'assistant' (your reply) and optionally 'taskcard'.\n\n"
    
    "AUTOMATION ANALYSIS:\n"
    "When someone describes a business process, analyze it for automation opportunities:\n"
    "- Identify repetitive tasks\n"
    "- Suggest specific automations\n"
    "- Recommend required services\n"
    "- Estimate time/money savings\n\n"
    
    "TASKCARD GENERATION:\n"
    "Create TaskCards for clear automation requests using these exact types:\n"
    "send_sms, book_appointment, update_crm, ingest_knowledge, repo_install, deploy, report_daily\n\n"
    
    "TaskCard structure: {\n"
    "  'type': 'send_sms',\n"
    "  'account_id': 'CLIENT_NAME',\n"
    "  'params': {'to': '+1234567890', 'body': 'message text'}\n"
    "}\n\n"
    
    "EXAMPLES:\n"
    "User: 'Text customers appointment confirmations'\n"
    "You: Suggest SMS automation + ask for template text and timing\n\n"
    
    "User: 'I run an HVAC company'\n"
    "You: Ask about current processes, suggest appointment reminders, follow-ups, seasonal maintenance\n\n"
    
    "Focus on building complete automation systems, not just individual tasks."
)

async def llm_chat(message: str, account_id: Optional[str], history: list = None) -> ChatOut:
    """Minimal LLM router: OpenAI by default. Returns ChatOut with optional TaskCard."""
    # Build conversation context with history
    prompt = [{"role": "system", "content": SYSTEM}]
    
    # Add conversation history if available
    if history:
        for msg in history[-10:]:  # Last 10 messages for context
            prompt.append({"role": msg["role"], "content": msg["content"]})
    
    # Add current message
    prompt.append({"role": "user", "content": json.dumps({"message": message, "account_id": account_id})})
    content = None

    if PROVIDER == "openai":
        if not OPENAI_KEY:
            raise HTTPException(500, "Missing OPENAI_API_KEY")
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=prompt,
            response_format={"type": "json_object"},
            temperature=0.4,
        )
        content = resp.choices[0].message.content

    elif PROVIDER == "anthropic":
        if not ANTH_KEY:
            raise HTTPException(500, "Missing ANTHROPIC_API_KEY")
        import anthropic
        ac = anthropic.Anthropic(api_key=ANTH_KEY)
        msg = ac.messages.create(
            model="claude-3-5-sonnet-20240620",
            system=SYSTEM,
            max_tokens=800,
            temperature=0.4,
            messages=[{"role":"user","content": json.dumps({"message": message, "account_id": account_id})}],
        )
        # Anthropic returns a content list; join text parts
        content = "".join(part.text for part in msg.content if getattr(part, "type", "text") == "text")

    else:
        raise HTTPException(500, f"Unsupported PROVIDER: {PROVIDER}")

    # Parse JSON payload {"assistant": str, "taskcard": {...}} safely
    try:
        data = json.loads(content)
        print(f"DEBUG: AI generated: {content}")  # Debug line
    except Exception:
        data = {"assistant": content, "taskcard": None}

    assistant = data.get("assistant") or ""
    tc = data.get("taskcard")
    taskcard = None
    if tc:
        try:
            taskcard = TaskCard.model_validate(tc)
        except ValidationError as e:
            assistant += f"\n\n(Note: Proposed TaskCard failed validation: {e.errors()[:2]})"
            print(f"DEBUG: Validation error: {e.errors()}")  # Debug line

    return ChatOut(assistant=assistant, taskcard=taskcard)

# ---- n8n dispatcher ----
async def dispatch_to_n8n(card: TaskCard) -> tuple[int, str]:
    if not (N8N_URL and N8N_TOKEN):
        raise HTTPException(500, "N8N_URL or N8N_TOKEN missing")
    
    # Wrap TaskCard in body object for n8n workflow compatibility
    payload = {"body": json.loads(card.model_dump_json())}
    
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{N8N_URL.rstrip('/')}/webhook/aiden-task",
            headers={
                "X-Aiden-Token": N8N_TOKEN, 
                "Content-Type": "application/json"
            },
            json=payload,
        )
    return r.status_code, r.text[:1000]

# ---- Routes ----
@app.get("/api/health")
def health():
    return {"ok": True, "app": APP_NAME, "provider": PROVIDER}

@app.post("/api/chat", response_model=ChatOut)
async def chat(body: ChatIn):
    account_id = body.account_id or "DEFAULT"
    
    # Check if this is a business with industry specified - use superintelligence
    if body.business_name and body.industry:
        try:
            # Create business key
            business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
            
            # Initialize business automation if not exists
            if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
                await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
                    business_name=body.business_name,
                    industry=body.industry,
                    context={"account_id": account_id}
                )
            
            # Have conversation with specialized AI assistant
            response_text = await AIDEN_SUPERINTELLIGENCE.business_conversation(
                business_key=business_key,
                message=body.message,
                context={"account_id": account_id}
            )
            
            # Log user and assistant messages
            await sb_upsert_message(account_id, "user", body.message)
            await sb_upsert_message(account_id, "assistant", response_text)
            
            return ChatOut(assistant=response_text, taskcard=None)
            
        except Exception as e:
            print(f"Superintelligence error: {e}")
            # Fall back to regular chat
            pass
    
    # Standard chat flow for general inquiries
    history = await sb_recent_messages(account_id)
    
    # Log user message
    await sb_upsert_message(account_id, "user", body.message)
    
    # Get AI response with history
    response = await llm_chat(body.message, body.account_id, history)
    
    # Log assistant message
    await sb_upsert_message(account_id, "assistant", response.assistant)
    
    return response

# ============================================================================
# 🎓 ADVANCED AIDEN CAPABILITIES - LEARNING & CUSTOM SOLUTIONS
# ============================================================================

class LearnPatternIn(BaseModel):
    business_name: str
    industry: str
    pattern_description: str
    examples: Optional[List[Dict[str, Any]]] = None
    account_id: Optional[str] = None

@app.post("/api/learn-pattern")
async def learn_new_automation_pattern(body: LearnPatternIn):
    """Teach Aiden a new automation pattern for any industry."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        # Initialize if needed
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
                business_name=body.business_name,
                industry=body.industry,
                context={"account_id": body.account_id}
            )
        
        # Learn the new pattern
        result = await AIDEN_SUPERINTELLIGENCE.learn_new_automation_pattern(
            business_key=business_key,
            pattern_description=body.pattern_description,
            examples=body.examples
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Learning error: {str(e)}")

class CustomSolutionIn(BaseModel):
    business_name: str
    industry: str
    client_need: str
    context: Optional[Dict[str, Any]] = None
    account_id: Optional[str] = None

@app.post("/api/create-solution")
async def create_custom_automation_solution(body: CustomSolutionIn):
    """Create a custom automation solution based on client needs."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        # Initialize if needed
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
                business_name=body.business_name,
                industry=body.industry,
                context={"account_id": body.account_id}
            )
        
        # Create custom solution
        result = await AIDEN_SUPERINTELLIGENCE.create_custom_automation_solution(
            business_key=business_key,
            client_need=body.client_need,
            context=body.context
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Solution creation error: {str(e)}")

class ImplementSolutionIn(BaseModel):
    business_name: str
    industry: str
    solution_id: str
    account_id: Optional[str] = None

@app.post("/api/implement-solution")
async def implement_custom_solution(body: ImplementSolutionIn):
    """Implement a previously designed custom automation solution."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            raise HTTPException(400, "Business not initialized")
        
        # Implement the solution
        result = await AIDEN_SUPERINTELLIGENCE.implement_custom_solution(
            business_key=business_key,
            solution_id=body.solution_id
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Implementation error: {str(e)}")

# ============================================================================
# 🌐 WEBSITE CREATION & DEPLOYMENT
# ============================================================================

class WebsiteSpecIn(BaseModel):
    business_name: str
    industry: str
    business_description: Optional[str] = None
    type: str = "landing_page"  # landing_page, full_website, blog
    style: str = "modern"  # modern, classic, minimalist, bold
    features: List[str] = []  # contact_form, blog, ecommerce, analytics
    include_blog: bool = True
    domain: Optional[str] = None
    account_id: Optional[str] = None

@app.post("/api/create-website")
async def create_website(body: WebsiteSpecIn):
    """Create a stunning website or landing page for a business."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        # Initialize if needed
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            await AIDEN_SUPERINTELLIGENCE.initialize_business_automation(
                business_name=body.business_name,
                industry=body.industry,
                context={"account_id": body.account_id}
            )
        
        # Create website
        website_spec = {
            "type": body.type,
            "style": body.style,
            "features": body.features,
            "include_blog": body.include_blog,
            "domain": body.domain,
            "business_description": body.business_description
        }
        
        result = await AIDEN_SUPERINTELLIGENCE.create_website(
            business_key=business_key,
            website_spec=website_spec
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Website creation error: {str(e)}")

class DeployWebsiteIn(BaseModel):
    business_name: str
    industry: str
    website_id: str
    platform: str = "vercel"  # vercel, netlify, aws, custom
    domain: Optional[str] = None
    ssl: bool = True
    cdn: bool = True
    account_id: Optional[str] = None

@app.post("/api/deploy-website")
async def deploy_website(body: DeployWebsiteIn):
    """Deploy a created website to the specified platform and domain."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            raise HTTPException(400, "Business not initialized")
        
        # Deploy website
        deployment_config = {
            "platform": body.platform,
            "domain": body.domain,
            "ssl": body.ssl,
            "cdn": body.cdn
        }
        
        result = await AIDEN_SUPERINTELLIGENCE.deploy_website(
            business_key=business_key,
            website_id=body.website_id,
            deployment_config=deployment_config
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Website deployment error: {str(e)}")

# ============================================================================
# 📚 CONTINUOUS LEARNING & INSIGHTS
# ============================================================================

class ClientInteractionIn(BaseModel):
    business_name: str
    industry: str
    client_id: str
    query: str
    solution: str
    feedback: Optional[str] = None
    outcome: Optional[str] = None
    preferred_solutions: Optional[List[str]] = None
    automation_goals: Optional[List[str]] = None
    feedback_score: Optional[int] = None
    account_id: Optional[str] = None

@app.post("/api/learn-from-interaction")
async def learn_from_client_interaction(body: ClientInteractionIn):
    """Learn from client interactions to improve automation solutions."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            raise HTTPException(400, "Business not initialized")
        
        # Prepare interaction data
        interaction_data = {
            "client_id": body.client_id,
            "query": body.query,
            "solution": body.solution,
            "feedback": body.feedback,
            "outcome": body.outcome,
            "preferred_solutions": body.preferred_solutions,
            "automation_goals": body.automation_goals,
            "feedback_score": body.feedback_score
        }
        
        # Learn from interaction
        result = await AIDEN_SUPERINTELLIGENCE.learn_from_client_interaction(
            business_key=business_key,
            interaction_data=interaction_data
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Learning error: {str(e)}")

class GenerateReportIn(BaseModel):
    business_name: str
    industry: str
    account_id: Optional[str] = None

@app.post("/api/generate-report")
async def generate_automation_report(body: GenerateReportIn):
    """Generate a comprehensive automation report for a business."""
    try:
        business_key = f"{body.business_name}_{body.industry}".lower().replace(" ", "_")
        
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            raise HTTPException(400, "Business not initialized")
        
        # Generate report
        result = await AIDEN_SUPERINTELLIGENCE.generate_automation_report(
            business_key=business_key
        )
        
        return {"success": True, "result": result, "business_key": business_key}
        
    except Exception as e:
        raise HTTPException(500, f"Report generation error: {str(e)}")

# ============================================================================
# 📊 BUSINESS STATUS & ANALYTICS
# ============================================================================

@app.get("/api/business-status/{business_name}/{industry}")
async def get_business_status(business_name: str, industry: str):
    """Get the current status and capabilities of a business's AI assistant."""
    try:
        business_key = f"{business_name}_{industry}".lower().replace(" ", "_")
        
        if business_key not in AIDEN_SUPERINTELLIGENCE.active_assistants:
            return {"status": "not_initialized", "message": "Business not yet set up"}
        
        assistant_info = AIDEN_SUPERINTELLIGENCE.active_assistants[business_key]
        
        status = {
            "business_name": assistant_info.get("business_name"),
            "industry": assistant_info.get("industry"),
            "created_at": str(assistant_info.get("created_at")),
            "learned_patterns": len(assistant_info.get("learned_patterns", [])),
            "custom_solutions": len(assistant_info.get("custom_solutions", {})),
            "websites": len(assistant_info.get("websites", {})),
            "client_preferences": len(assistant_info.get("client_preferences", {})),
            "assistant_id": assistant_info.get("id")
        }
        
        return {"success": True, "status": status}
        
    except Exception as e:
        raise HTTPException(500, f"Status check error: {str(e)}")

class TaskIn(BaseModel):
    taskcard: TaskCard
    pin: Optional[str] = None

@app.post("/api/task")
async def task(body: TaskIn):
    # PIN check disabled for dev/testing
    # if (body.pin or "").replace(" ", "") != DISPATCH_PIN:
    #     raise HTTPException(401, "PIN required or incorrect")
    code, txt = await dispatch_to_n8n(body.taskcard)
    return {"status": code, "body": txt}

# Create a zip of the project for download
EXCLUDE = [
    "*.pyc", "__pycache__/*", ".venv*", ".git*", "*.zip", "*.log", "node_modules*",
]

@app.get("/api/export")
async def export_zip():
    mem = io.BytesIO()
    with zipfile.ZipFile(mem, mode="w", compression=zipfile.ZIP_DEFLATED) as z:
        for path in ROOT.rglob("*"):
            rel = path.relative_to(ROOT).as_posix()
            if path.is_dir():
                continue
            # exclude patterns
            if any(fnmatch.fnmatch(rel, pat) for pat in EXCLUDE):
                continue
            # don't embed secrets; keep example
            if rel == ".env":
                continue
            z.write(path, arcname=rel)
    mem.seek(0)
    headers = {"Content-Disposition": "attachment; filename=aiden-replit-mvp.zip"}
    return StreamingResponse(mem, media_type="application/zip", headers=headers)

# --- Static UI mount (after API routes) ---
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False) 
def _root():
    # avoid catching /api/*; just send humans to the dashboard
    return RedirectResponse("/app")

app.mount("/app", StaticFiles(directory=ROOT / "public", html=True), name="public")