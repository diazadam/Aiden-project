# 🤖 INTEGRATE YOUR OPENAI ASSISTANT WITH AIDEN

## Step 1: Get Your Assistant ID

1. Go to [OpenAI Platform Assistants](https://platform.openai.com/assistants)
2. Find your assistant: `asst_mmCt54r7HpOgR5hQFaNhyDks` 
3. Copy the exact Assistant ID from the platform

## Step 2: Update the Code

Edit `superintelligence.py` line 45:

```python
# Replace this line:
self.existing_assistant_id = "asst_mmCt54r7HpOgR5hQFaNhyDks"

# With your correct assistant ID:
self.existing_assistant_id = "YOUR_ACTUAL_ASSISTANT_ID"
```

## Step 3: Use Your Assistant

### Option A: Use Your Assistant for All Conversations

Edit `main.py` line 309 to always use your assistant:

```python
# Replace this:
response_text = await AIDEN_SUPERINTELLIGENCE.business_conversation(
    business_key=business_key,
    message=body.message,
    context={"account_id": account_id}
)

# With this:
response_text = await AIDEN_SUPERINTELLIGENCE.business_conversation(
    business_key=business_key,
    message=body.message,
    context={"account_id": account_id},
    use_existing_assistant=True  # 👈 This uses YOUR assistant
)
```

### Option B: Create a Direct Endpoint for Your Assistant

Add this to `main.py`:

```python
@app.post("/api/your-assistant")
async def your_assistant_chat(body: ChatIn):
    """Direct endpoint for your OpenAI Assistant"""
    account_id = body.account_id or "DEFAULT"
    
    # Use your assistant directly
    response_text = await AIDEN_SUPERINTELLIGENCE.aiden_core.use_existing_assistant(
        message=body.message,
        context={"account_id": account_id}
    )
    
    # Log conversation
    await sb_upsert_message(account_id, "user", body.message)
    await sb_upsert_message(account_id, "assistant", response_text)
    
    return ChatOut(assistant=response_text, taskcard=None)
```

## Step 4: Test Integration

Run this command to test:

```bash
source venv/bin/activate && python use_existing_assistant.py
```

## Step 5: Configure Your Assistant

To maximize compatibility with Aiden, configure your assistant with:

### System Instructions:
```
You are Aiden, an expert AI business automation consultant. You help users build automation systems for their businesses.

Focus on:
- Understanding business processes and automation opportunities
- Providing specific, actionable recommendations
- Suggesting automation workflows and integrations
- Being enthusiastic about helping businesses grow through automation

Always ask follow-up questions to better understand the user's business needs.
```

### Recommended Tools:
- ✅ **File Search**: For knowledge retrieval
- ✅ **Code Interpreter**: For calculations and data analysis
- ✅ **Functions**: Add custom functions for business integrations

## Integration Benefits

Once integrated, your assistant will:
- 🧠 **Remember conversations** across the Control Tower interface
- 🔧 **Execute function calls** for direct API integrations  
- 🎯 **Handle business-specific queries** with your custom training
- 📊 **Integrate with n8n workflows** for automation deployment

## Troubleshooting

**Assistant not found (404 error)?**
- Verify the assistant ID is correct
- Check you're using the right OpenAI API key
- Ensure the assistant exists in the same project/organization

**No response from assistant?**
- Check your OpenAI API key has Assistants API access
- Verify your account has sufficient credits
- Look for error messages in the console output

**Function calls not working?**
- Make sure your assistant has Functions tool enabled
- Check the function definitions match between your assistant and our code
- Verify the function calling permissions

---

🚀 **Ready to integrate?** Update the assistant ID and test the connection!