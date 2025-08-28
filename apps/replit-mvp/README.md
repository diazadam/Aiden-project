# Aiden Control Tower - Replit MVP

A modern web dashboard for AI-powered task orchestration with natural language to structured TaskCard conversion and secure n8n webhook dispatch.

## Features

- 🤖 **Natural Language Processing**: Convert plain text requests into structured TaskCards using OpenAI GPT-4o-mini or Anthropic Claude
- 🛡️ **PIN-Protected Dispatch**: Secure approval workflow with PIN verification before task execution
- 🎯 **n8n Integration**: Direct webhook dispatch to n8n workflows with custom token authentication
- 📱 **Modern UI**: Dark theme, responsive design, real-time chat interface
- 📦 **Project Export**: Download complete project as ZIP for local deployment
- 🔍 **Health Monitoring**: Real-time system status and provider information

## Quick Start on Replit

1. **Import to Replit**:
   - Upload this folder to a new Replit project
   - Replit will automatically detect Python and configure the environment

2. **Configure Environment**:
   - Copy `.env.example` to `.env`
   - Fill in your API keys and n8n configuration:
   ```bash
   cp .env.example .env
   ```

3. **Set Required Variables**:
   ```env
   PROVIDER=openai  # or "anthropic"
   OPENAI_API_KEY=sk-your-key-here
   N8N_URL=https://your-n8n-instance.com
   N8N_TOKEN=your-webhook-token
   DISPATCH_PIN=4242
   ```

4. **Run**:
   - Click the "Run" button in Replit
   - The app will start on port 8080 and be accessible via your Replit URL

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run server
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

## Architecture

### TaskCard Schema
Structured JSON format for task dispatch:
```json
{
  "trace_id": "optional-tracking-id",
  "account_id": "ACME-HVAC", 
  "type": "send_sms",
  "source": "dashboard",
  "params": {
    "to": "+15551234567",
    "body": "Your HVAC is booked for tomorrow 9-11am"
  }
}
```

### Supported Task Types
- `send_sms` - SMS messaging
- `book_appointment` - Calendar scheduling  
- `update_crm` - CRM record updates
- `ingest_knowledge` - Knowledge base additions
- `repo_install` - Code repository setup
- `deploy` - Application deployment
- `report_daily` - Automated reporting

## API Endpoints

- `GET /api/health` - System health check
- `POST /api/chat` - Natural language to TaskCard conversion
- `POST /api/task` - PIN-protected task dispatch to n8n
- `GET /api/export` - Download project ZIP

## n8n Webhook Setup

Your n8n workflow should expect:
- **URL**: `{N8N_URL}/webhook/aiden-task`
- **Headers**: `X-Aiden-Token: {N8N_TOKEN}`
- **Body**: TaskCard JSON payload

Example n8n webhook node configuration:
```json
{
  "httpMethod": "POST",
  "path": "aiden-task",
  "options": {},
  "authentication": "headerAuth",
  "headerAuth": {
    "name": "X-Aiden-Token",
    "value": "your-token-here"
  }
}
```

## Security Features

- PIN-protected task dispatch prevents unauthorized execution
- Environment-based configuration keeps secrets secure  
- Token-based n8n authentication
- Input validation and sanitization

## Usage Examples

1. **Simple SMS**:
   - Input: "Text +15551234567: Your appointment is confirmed"
   - Result: TaskCard with type `send_sms` and populated phone/message

2. **Appointment Booking**:
   - Input: "Book John Smith for HVAC service tomorrow 9-11am"
   - Result: TaskCard with type `book_appointment` and service details

3. **CRM Update**:
   - Input: "Update lead 12345 status to qualified"
   - Result: TaskCard with type `update_crm` and lead information

## Customization

- **Add Task Types**: Extend the `TaskCard.type` enum in `main.py`
- **Modify UI**: Edit `public/index.html` for custom styling
- **LLM Prompts**: Adjust the `SYSTEM` prompt for different behavior
- **Export Rules**: Modify `EXCLUDE` patterns for ZIP generation

## Production Deployment

For production use:
1. Use environment variables instead of `.env` file
2. Configure proper reverse proxy (nginx/CloudFlare)
3. Enable HTTPS with SSL certificates
4. Set up monitoring and logging
5. Consider rate limiting and authentication

## Integration with Aiden Project

This MVP is designed to integrate with the larger Aiden ecosystem:
- Shares TaskCard schema with other Aiden components
- Compatible with host executor security model
- Uses consistent environment variable patterns
- Follows established architectural conventions