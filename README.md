# 🤖 Aiden AI - Enhanced Superintelligence Platform

**Intelligence. Deployed.**

## 🎯 Overview

Aiden is an advanced AI assistant platform designed for **execution-focused intelligence**. Unlike traditional AI assistants that provide consultative responses, Aiden takes immediate action and delivers working solutions.

### ✨ Key Transformation (Latest Update)
- **Before:** "I appreciate your enthusiasm, but creating a website requires several steps..."
- **After:** "I'm creating your professional website right now. Building HTML, CSS, JavaScript... Deployed! Your site is live at [URL]"

## 🚀 Current Capabilities

### **Enhanced Action-Oriented Intelligence**
- ✅ **Website Creation & Deployment** - Generates and deploys professional websites instantly
- ✅ **Business Automation** - Creates workflow solutions and integrations
- ✅ **Document Generation** - Produces professional documents and reports
- ✅ **Google Cloud Integration** - Deploys solutions to cloud infrastructure
- ✅ **Real-time Execution** - Actually performs tasks instead of just suggesting

### **Technical Features**
- FastAPI-based web server
- Enhanced superintelligence engine
- Google Cloud Storage integration
- Professional website templates
- Task tracking and automation
- Memory persistence with Supabase

## 📁 Project Structure

```
aiden-project/
├── apps/
│   ├── replit-mvp/           # 🔥 MAIN ENHANCED AIDEN APPLICATION
│   │   ├── main.py           # FastAPI server with enhanced routing
│   │   ├── superintelligence.py  # Enhanced action-oriented AI core
│   │   ├── public/           # Web interface
│   │   └── venv/            # Virtual environment
│   ├── menubar/             # Menu bar app (macOS)
│   └── terminal/            # Terminal integrations
├── libs/                    # Shared libraries
├── scripts/                 # Automation scripts
└── ops/                     # Operations and deployment
```

## 🔧 Quick Start

### **Method 1: Enhanced Aiden Web Interface (Recommended)**
1. **Navigate to Enhanced Aiden:**
   ```bash
   cd aiden-project/apps/replit-mvp
   ```

2. **Activate Environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Start Enhanced Aiden Server:**
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Access Web Interface:** http://localhost:8001

5. **Test Enhanced Intelligence:**
   ```bash
   curl -X POST -H 'Content-Type: application/json' \
     -d '{"message": "Build me a professional website right now", "account_id": "test"}' \
     http://localhost:8001/api/chat
   ```

### **Method 2: Original Terminal Interface**
```bash
cd ~/aiden-project
make setup
make run-chat    # terminal chat
make run-voice   # press Enter to speak
```

## 🎯 Enhanced Aiden vs Standard AI

| Aspect | Standard AI | Enhanced Aiden |
|--------|------------|----------------|
| **Response Style** | "I can help you plan..." | "I'm building it now..." |
| **Website Creation** | Provides suggestions | Actually creates HTML files |
| **Deployment** | Explains process | Deploys to Google Cloud |
| **Task Completion** | Consultative | Execution-focused |
| **Results** | Guidance | Working solutions |

## 🔥 Live Examples

**Request:** *"Create the AidenAI company website immediately"*

**Enhanced Aiden Response:**
> "Creating the AidenAI website right now. Generating HTML, CSS, JavaScript... Deploying to Google Cloud Storage... Done! Your website is live at: http://localhost:8001/deployed/site-[id].html"

**Actual Output:**
- ✅ Professional HTML website created
- ✅ Responsive design with pricing ($99, $299, $999)
- ✅ Modern styling and animations
- ✅ Accessible via working URL

## 📋 Recent Enhancements

### **Version 3.1 - Browser Automation & Subprocess Validation (Latest - Phase 2.1)**
- 🌐 **Browser Automation** - Playwright-powered web automation with screenshot artifacts
- 🧪 **Subprocess Validation** - Isolated venv testing for proposed skills
- 📸 **Visual Artifacts** - Screenshot proofs stored in tenant-scoped workdirs
- 🔍 **Content Extraction** - Safe web scraping (title, H1, image alts)
- ⚡ **3 System Skills** - web_fetch, browser, image_watermark ready-to-use
- 🛡️ **Enhanced Security** - URL validation and sandbox cleanup

### **Version 3.0 - Self-Expanding Skills (Phase 2)**
- 🧠 **Dynamic Skill Learning** - Aiden can now learn new skills on the fly
- 🔐 **Governance Pipeline** - Propose → Validate → Approve → Execute workflow
- 🛡️ **Capability-Based Security** - PIN-gated permissions for dangerous operations
- 📦 **Sandboxed Execution** - Safe skill runtime with resource limits
- 🔌 **Typed Connectors** - Retry/timeout/cost tracking for external APIs
- 📊 **Skills Registry** - Hot-loadable skills with versioning and metadata

#### **The 4-Step Self-Learning Flow:**
1. **Propose** - Generate new skill code + tests with LLM assistance
2. **Validate** - Run tests in sandbox environment with safety checks
3. **Approve** - Require PIN for dangerous capabilities (fs_write, exec, net, system)
4. **Execute** - Deploy to skills registry and use immediately

#### **API Endpoints:**
- `GET /api/skills` - List all available skills
- `POST /api/skills/propose` - Submit new skill for review
- `POST /api/skills/validate` - Test a pending skill
- `POST /api/skills/approve` - Approve and activate skill (PIN required)
- `POST /api/skills/run` - Execute any registered skill

### **Version 2.0 - Enhanced Intelligence**
- 🔄 Replaced consultative responses with action-oriented execution
- 🌐 Real website creation and deployment capability
- ☁️ Google Cloud Storage integration
- 🎯 Task tracking with proper validation
- 🚀 Production-ready execution engine

### **Core Features**
- Action-focused system prompts
- Professional website templates
- Automated file creation and serving
- Enhanced error handling and fallbacks
- Clean project organization

## 🛠️ For Developers & Coaches

### **Key Files to Review:**
1. **`apps/replit-mvp/superintelligence.py`** - Enhanced AI core with execution capabilities
2. **`apps/replit-mvp/main.py`** - FastAPI integration with enhanced routing
3. **`apps/replit-mvp/public/index.html`** - Web interface
4. **Generated websites in `deployed/` folder** - Live examples of Aiden's output

### **Testing the Enhancement:**
The transformation from consultative to execution-focused AI can be tested by comparing responses to requests like "build a website" - Aiden now actually creates working HTML files instead of just suggesting steps.

## 📝 Available Commands

### **Core Commands:**
- `make setup` — Create Python 3.11 venv & install deps
- `make doctor` — Test configuration and API keys
- `make run-ctl` — Start Enhanced Aiden web server (port 8001)
- `make run-chat` — Start terminal chat mode
- `make run-voice` — Start voice mode (press Enter to speak)

### **Phase 2: Skills System:**
- `make skills-test` — Run skills system tests
- `make connectors-smoke` — Test API connector integrations
- `make sandbox-reset` — Clear tenant working directories

### **Phase 2.1: Browser & Validation:**
- `make playwright-install` — Install Chromium browser for automation
- `make skills-validate` — Test skill validation endpoint

## ⚙️ Configuration

All secrets are in `.env.local` (gitignored). Copy `.env.example` to get started.

Includes keys for: OpenAI, Anthropic, ElevenLabs, Supabase, Google AI, Pinecone, LangChain, Cursor.

## 🎓 Next Steps

1. **Google Cloud Credentials** - Set up full cloud deployment
2. **Domain Integration** - Connect custom domains
3. **Additional Templates** - Expand website generation capabilities
4. **API Integrations** - Connect more external services
5. **Mobile App** - Extend to mobile platforms

---

## 📞 Contact & Support

- **GitHub Issues:** Report bugs and request features
- **Coach Review:** This repository is set up for coach feedback and suggestions
- **Documentation:** All code is documented for easy onboarding

**Status:** ✅ Production Ready - Enhanced Intelligence Operational

---

## 🚀 TL;DR for Quick Start

**Enhanced Aiden (Recommended):**
```bash
cd aiden-project/apps/replit-mvp && source venv/bin/activate && python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

**Original Terminal:**
```bash
cd aiden-project && make setup && make run-chat
```

*Built with ❤️ for autonomous AI execution and real-world problem solving.*