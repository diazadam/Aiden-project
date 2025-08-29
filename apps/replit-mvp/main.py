import os, io, json, zipfile, fnmatch, shutil, hashlib
from typing import Optional, Literal, List, Dict, Any
from pathlib import Path
from datetime import datetime

import httpx
from fastapi import FastAPI, Request, HTTPException, APIRouter
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv

# Import enhanced superintelligence
from superintelligence import AIDEN_SUPERINTELLIGENCE_ENHANCED, AIDEN_SUPERINTELLIGENCE

# Import skills system
from skills.registry import REGISTRY, Manifest, APPROVED_DIR, PENDING_DIR, AUDIT_LOG
from skills.runtime import run_skill
from skills.validate_pending import validate_pending_skill
from security.policies import SECRET_PIN, CapsPolicy
from connectors.openai_llm import OpenAIChat

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

# Load skills registry at startup
@app.on_event("startup")
async def _load_skills():
    REGISTRY.load_all()
    print("[skills] loaded:", REGISTRY.list())

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

# ---- Skills System Routes ----
class ProposeBody(BaseModel):
    name: str
    description: str = ""
    version: str = "0.1.0"
    caps: List[str] = []
    code: str
    tests: Optional[str] = None

@app.get("/api/skills")
def list_skills():
    """List all available skills with their metadata"""
    return {"skills": REGISTRY.list()}

@app.post("/api/skills/propose")
def propose_skill(body: ProposeBody, account_id: str = "local"):
    """Propose a new skill for validation and approval"""
    # Write to pending directory
    skill_dir = os.path.join(PENDING_DIR, body.name)
    if os.path.exists(skill_dir):
        shutil.rmtree(skill_dir)
    os.makedirs(skill_dir, exist_ok=True)
    
    # Save skill code
    code_path = os.path.join(skill_dir, "skill.py")
    with open(code_path, "w") as f:
        f.write(body.code)
    
    # Generate checksum and manifest
    checksum = hashlib.sha256(body.code.encode()).hexdigest()
    manifest = Manifest(
        name=body.name, 
        version=body.version, 
        caps=body.caps, 
        description=body.description, 
        checksum=checksum
    )
    
    with open(os.path.join(skill_dir, "manifest.json"), "w") as f:
        f.write(manifest.model_dump_json(indent=2))
    
    # Save tests if provided
    if body.tests:
        tests_dir = os.path.join(skill_dir, "tests")
        os.makedirs(tests_dir, exist_ok=True)
        with open(os.path.join(tests_dir, f"test_{body.name}.py"), "w") as f:
            f.write(body.tests)
    
    # Log proposal
    with open(AUDIT_LOG, "a") as log:
        log.write(json.dumps({
            "event": "propose",
            "name": body.name,
            "by": account_id,
            "timestamp": datetime.now().isoformat()
        }) + "\n")
    
    return {"ok": True, "pending_path": skill_dir}

class ValidateBody(BaseModel):
    name: str

@app.post("/api/skills/validate")
def validate_skill(body: ValidateBody):
    """Validate a pending skill using subprocess isolation and testing"""
    res = validate_pending_skill(body.name)
    if not res.get("ok"):
        raise HTTPException(400, json.dumps(res))
    return res

class ApproveBody(BaseModel):
    name: str
    pin: str

@app.post("/api/skills/approve")
def approve_skill(body: ApproveBody, account_id: str = "local"):
    """Approve a pending skill (requires PIN for dangerous capabilities)"""
    if body.pin != SECRET_PIN:
        raise HTTPException(401, "invalid pin")
    
    pending = os.path.join(PENDING_DIR, body.name)
    if not os.path.isdir(pending):
        raise HTTPException(404, "pending skill not found")
    
    approved = os.path.join(APPROVED_DIR, body.name)
    if os.path.exists(approved):
        shutil.rmtree(approved)
    
    shutil.copytree(pending, approved)
    
    # Refresh registry
    REGISTRY.load_all()
    
    # Log approval
    with open(AUDIT_LOG, "a") as log:
        log.write(json.dumps({
            "event": "approve",
            "name": body.name,
            "by": account_id,
            "timestamp": datetime.now().isoformat()
        }) + "\n")
    
    return {"ok": True, "message": f"approved {body.name}", "skills": REGISTRY.list()}

class RunSkillBody(BaseModel):
    name: str
    args: Dict[str, Any] = {}
    pin: Optional[str] = None
    account_id: str = "local"

@app.post("/api/skills/run")
def run_skill_endpoint(body: RunSkillBody):
    """Execute a skill with given parameters"""
    token = body.pin if body.pin else None
    result = run_skill(body.name, body.account_id, body.args, caps_token=token)
    return result.model_dump()

class ProposeFromPromptBody(BaseModel):
    name: str
    description: str = ""
    caps: List[str] = []     # suggested caps (we still PIN gate dangerous)
    prompt: str              # plain English description / spec
    version: str = "0.1.0"

SKILL_SYSTEM_SPEC = """
You are generating a Python skill for the Aiden Skills framework.

Rules:
- File must be named skill.py and define class SkillImpl(Skill) with:
  - name: str (match the proposed name)
  - version: "0.1.0" (or provided)
  - caps: set[str] (only what's necessary: fs_write, net, exec, system)
  - Inputs(BaseModel), Outputs(BaseModel)
  - def run(self, ctx: SkillContext, args: Inputs) -> Outputs
- Import from 'skills.contracts' (absolute) for Skill, SkillInputs, SkillOutputs, SkillContext.
- NO external network calls unless caps includes 'net'.
- If writing files, write ONLY to ctx.workdir.
- Keep code under 200 lines if possible; keep dependencies minimal.

Also generate a short pytest file content (optional) that imports your skill via
'from skills._sandboxed.<NAME>.skill import SkillImpl' and tests run().
Return JSON with fields: code (string), tests (string or empty).
"""

@app.post("/api/skills/propose_from_prompt")
def propose_from_prompt(body: ProposeFromPromptBody, account_id: str = "local"):
    """Generate a skill from plain English using LLM"""
    try:
        llm = OpenAIChat()
        sys_msg = "You write safe, minimal Python plugins for Aiden Skills."
        user_prompt = f"""
Write a new skill named '{body.name}' (version {body.version}) with caps {body.caps}.
Description: {body.description}

Spec (user intent):
{body.prompt}

Follow the SKILL_SYSTEM_SPEC strictly and return JSON with keys code, tests.
SKILL_SYSTEM_SPEC:
{SKILL_SYSTEM_SPEC}
"""
        resp = llm.complete(prompt=user_prompt, system=sys_msg)
        if not resp.ok:
            raise HTTPException(500, f"LLM error: {resp.message}")

        # Parse JSON in model output (model may emit text; try to find the JSON block)
        import re
        txt = resp.data.strip()
        # naive JSON detection
        m = re.search(r'\{[\s\S]*\}', txt)
        if not m:
            raise HTTPException(400, "LLM did not return JSON")
        try:
            j = json.loads(m.group(0))
        except Exception as e:
            raise HTTPException(400, f"JSON parse error: {e}")

        # Build manifest + write pending
        pending = os.path.join(PENDING_DIR, body.name)
        if os.path.exists(pending):
            shutil.rmtree(pending)
        os.makedirs(pending, exist_ok=True)

        code = j.get("code","")
        tests = j.get("tests","")
        if not code:
            raise HTTPException(400, "Generated code empty")

        code_path = os.path.join(pending, "skill.py")
        with open(code_path, "w") as f:
            f.write(code)

        checksum = hashlib.sha256(code.encode()).hexdigest()
        manifest = Manifest(name=body.name, version=body.version, caps=body.caps, description=body.description, checksum=checksum)
        with open(os.path.join(pending, "manifest.json"), "w") as f:
            f.write(manifest.model_dump_json(indent=2))

        if tests:
            os.makedirs(os.path.join(pending, "tests"), exist_ok=True)
            with open(os.path.join(pending, "tests", f"test_{body.name}.py"), "w") as f:
                f.write(tests)

        # Log proposal
        with open(AUDIT_LOG, "a") as log:
            log.write(json.dumps({
                "event": "propose_from_prompt",
                "name": body.name,
                "by": account_id,
                "timestamp": datetime.now().isoformat()
            }) + "\n")

        return {"ok": True, "pending_path": pending, "hint": "Run /api/skills/validate then /approve"}

    except Exception as e:
        raise HTTPException(500, f"Skill generation failed: {str(e)}")

# ---- Core API Routes ----
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
    
    # Enhanced Aiden execution mode for general requests
    try:
        # Log user message
        await sb_upsert_message(account_id, "user", body.message)
        
        # Use enhanced execution-focused Aiden
        enhanced_response = await AIDEN_SUPERINTELLIGENCE_ENHANCED(body.message, account_id)
        
        # Log assistant message
        await sb_upsert_message(account_id, "assistant", enhanced_response["assistant"])
        
        return ChatOut(
            assistant=enhanced_response["assistant"], 
            taskcard=enhanced_response.get("taskcard")
        )
        
    except Exception as e:
        # Fall back to standard chat flow
        history = await sb_recent_messages(account_id)
        response = await llm_chat(body.message, body.account_id, history)
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

# ============================================================================
# 📱 SMS INTEGRATION TEST ENDPOINT
# ============================================================================

class SMSTestIn(BaseModel):
    to_number: str = Field(..., description="Phone number to send test SMS (include country code)")
    message: Optional[str] = "🤖 Aiden SMS Test: Your Twilio integration is working!"

@app.post("/api/sms/test")
async def test_sms_sending(body: SMSTestIn):
    """Test SMS sending capability using Twilio credentials"""
    
    # Check for Twilio environment variables
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    if not account_sid or not auth_token:
        return {
            "success": False,
            "error": "Twilio credentials not configured",
            "setup_required": {
                "variables": ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN"],
                "guide": "Add these to your .env.local file"
            }
        }
    
    try:
        # Import and test Twilio
        from twilio.rest import Client
        
        client = Client(account_sid, auth_token)
        
        # Get available phone numbers
        phone_numbers = client.incoming_phone_numbers.list(limit=1)
        if not phone_numbers:
            return {
                "success": False,
                "error": "No Twilio phone number found",
                "setup_required": {
                    "action": "Purchase a phone number in your Twilio console",
                    "url": "https://console.twilio.com/us1/develop/phone-numbers/manage/incoming"
                }
            }
        
        from_number = phone_numbers[0].phone_number
        
        # Format phone number
        to_number = body.to_number
        if not to_number.startswith('+'):
            if to_number.startswith('1'):
                to_number = '+' + to_number
            else:
                to_number = '+1' + to_number
        
        # Send test message
        message = client.messages.create(
            body=body.message,
            from_=from_number,
            to=to_number
        )
        
        return {
            "success": True,
            "message_sid": message.sid,
            "status": message.status,
            "to": message.to,
            "from": message.from_,
            "body": message.body,
            "sent_at": datetime.now().isoformat(),
            "twilio_account": account_sid[:8] + "..."
        }
        
    except ImportError:
        return {
            "success": False,
            "error": "Twilio SDK not installed",
            "setup_required": {
                "action": "Install Twilio SDK",
                "command": "pip install twilio>=9.0.0"
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"SMS sending failed: {str(e)}",
            "debug_info": {
                "account_sid": account_sid[:8] + "..." if account_sid else "missing",
                "to_number": to_number,
                "from_number": from_number if 'from_number' in locals() else "unknown"
            }
        }

# --- Static UI mount (after API routes) ---
from fastapi.responses import RedirectResponse

@app.get("/", include_in_schema=False)
@app.head("/", include_in_schema=False) 
def _root():
    # avoid catching /api/*; just send humans to the dashboard
    return RedirectResponse("/app")

app.mount("/app", StaticFiles(directory=ROOT / "public", html=True), name="public")
# ===== AIDEN GOOGLE CLOUD DEPLOYMENT SYSTEM =====
import tempfile
import time
from google.cloud import storage
from google.cloud.exceptions import GoogleCloudError

# Global task tracking for interrupts
running_tasks = {}

@app.post("/api/stop")
async def emergency_stop():
    """Emergency stop all running operations"""
    global running_tasks
    stopped_count = len([t for t in running_tasks.values() if hasattr(t, 'cancel') and not t.done()])
    
    for task in running_tasks.values():
        if hasattr(task, 'cancel') and not task.done():
            task.cancel()
    
    running_tasks.clear()
    return {"ok": True, "message": f"🛑 Stopped {stopped_count} operations", "stopped": stopped_count}

@app.post("/api/deploy-website")
async def deploy_website_to_gcp(request: dict):
    """Deploy website to Google Cloud Storage with public access"""
    try:
        content = request.get("content", "")
        site_name = request.get("name", f"aiden-site-{int(time.time())}")
        
        if not content:
            return {"ok": False, "error": "No content provided"}
        
        # Initialize Google Cloud Storage client
        client = storage.Client()
        bucket_name = f"{site_name}-{int(time.time())}".lower()
        
        # Create a new bucket
        bucket = client.create_bucket(bucket_name, location="US")
        
        # Upload the website content
        blob = bucket.blob("index.html")
        blob.upload_from_string(content, content_type='text/html')
        
        # Make the file publicly accessible
        blob.make_public()
        
        # Set bucket to serve as website
        bucket.iam.grant_all_users_view_permission()
        
        public_url = f"https://storage.googleapis.com/{bucket_name}/index.html"
        
        return {
            "ok": True,
            "message": "🚀 Website deployed to Google Cloud!",
            "url": public_url,
            "bucket": bucket_name,
            "status": "deployed"
        }
        
    except GoogleCloudError as e:
        return {
            "ok": False, 
            "error": f"Google Cloud error: {str(e)}",
            "fallback_note": "Check your Google Cloud credentials and permissions"
        }
    except Exception as e:
        return {"ok": False, "error": f"Deployment error: {str(e)}"}

@app.post("/api/clone-and-deploy")  
async def clone_and_deploy_website(request: dict):
    """Clone a website and deploy it to Google Cloud"""
    try:
        url = request.get("url", "")
        site_name = request.get("name", f"cloned-site-{int(time.time())}")
        
        if not url:
            return {"ok": False, "error": "No URL provided"}
            
        # Use wget to clone the website
        import subprocess
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Clone website using wget
            result = subprocess.run([
                "wget", "--mirror", "--convert-links", "--adjust-extension", 
                "--page-requisites", "--no-parent", "--directory-prefix", temp_dir, url
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                return {"ok": False, "error": f"Failed to clone website: {result.stderr}"}
            
            # Find the main HTML file
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.html'):
                        with open(os.path.join(root, file), 'r', encoding='utf-8') as f:
                            content = f.read()
                        break
            else:
                return {"ok": False, "error": "No HTML file found in cloned website"}
            
            # Deploy to Google Cloud
            deploy_result = await deploy_website_to_gcp({"content": content, "name": site_name})
            return deploy_result
            
    except Exception as e:
        return {"ok": False, "error": f"Clone and deploy error: {str(e)}"}

# Serve deployed files locally as fallback
import os
os.makedirs("deployed", exist_ok=True)
app.mount("/deployed", StaticFiles(directory="deployed"), name="deployed")

