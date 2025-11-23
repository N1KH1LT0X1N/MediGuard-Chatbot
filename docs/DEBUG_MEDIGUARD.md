# 🐛 MediGuard Bot Debugging Guide

## Current Status ✅

All fixes have been applied to `mediguard_bot.py`:

1. ✅ Root route (`/`) now handles POST requests with helpful error message
2. ✅ `/whatsapp` endpoint has comprehensive error handling and logging
3. ✅ Debug endpoint (`/debug`) added for troubleshooting
4. ✅ All imports verified and working

## Routes Available

| Endpoint | Methods | Purpose |
|----------|---------|---------|
| `/` | GET, POST | Root endpoint (POST returns helpful error) |
| `/whatsapp` | POST | **Main webhook endpoint for Twilio** |
| `/health` | GET | Health check |
| `/debug` | GET, POST | Debug endpoint to inspect requests |

## Common Issues & Solutions

### Issue 1: 405 Method Not Allowed on `/`

**Error:**
```
127.0.0.1 - - [22/Nov/2025 23:26:55] "POST / HTTP/1.1" 405 -
```

**Cause:** Twilio webhook URL is configured to `/` instead of `/whatsapp`

**Solution:**
1. Go to Twilio Console → Messaging → Settings → WhatsApp Sandbox
2. Update "When a message comes in" to: `https://your-ngrok-url.ngrok.io/whatsapp`
3. Make sure it ends with `/whatsapp` (not just `/`)

**What happens now:**
- POST to `/` will return a 400 error with helpful message
- Console will show: `⚠️ WARNING: Received POST request to / instead of /whatsapp`

### Issue 2: No Response from Bot

**Symptoms:** Messages sent but no reply

**Debug Steps:**
1. Check if bot is running:
   ```bash
   curl http://localhost:5000/health
   ```

2. Check debug endpoint:
   ```bash
   curl http://localhost:5000/debug
   ```

3. Check bot logs for:
   ```
   📨 Received message from whatsapp:+1234567890: ...
   ✅ Sent response (1 chunk(s))
   ```

4. Verify Twilio webhook URL includes `/whatsapp`

### Issue 3: Database Errors

**Symptoms:** SQLite errors or permission issues

**Solution:**
```bash
# Check database file
ls -l mediguard.db

# Remove and recreate (will be auto-created)
rm mediguard.db
python mediguard_bot.py
```

## Testing Locally

### 1. Start the Bot
```bash
python mediguard_bot.py
```

Expected output:
```
MediGuard AI Bot starting on port 5000...
 * Running on http://0.0.0.0:5000
```

### 2. Test Root Endpoint (GET)
```bash
curl http://localhost:5000/
```

Expected:
```
MediGuard AI WhatsApp Bot is running. 🏥
```

### 3. Test Root Endpoint (POST) - Should show error
```bash
curl -X POST http://localhost:5000/
```

Expected:
```json
{
  "error": "Webhook endpoint is /whatsapp, not /",
  "message": "Please configure Twilio webhook URL to: https://your-domain.com/whatsapp",
  "current_path": "/",
  "correct_path": "/whatsapp"
}
```

### 4. Test Health Check
```bash
curl http://localhost:5000/health
```

Expected:
```json
{"status": "healthy", "service": "mediguard-bot"}
```

### 5. Test Debug Endpoint
```bash
curl http://localhost:5000/debug
```

### 6. Test WhatsApp Webhook (Simulate Twilio)
```bash
curl -X POST http://localhost:5000/whatsapp \
  -d "From=whatsapp:+1234567890" \
  -d "Body=hello"
```

Expected console output:
```
📨 Received message from whatsapp:+1234567890: hello...
✅ Sent response (1 chunk(s))
```

### 7. Test with ngrok

1. Start bot: `python mediguard_bot.py`
2. Start ngrok: `ngrok http 5000`
3. Copy HTTPS URL (e.g., `https://abcd1234.ngrok.io`)
4. Configure Twilio: `https://abcd1234.ngrok.io/whatsapp`
5. Send test message from WhatsApp

## Log Messages to Watch For

### ✅ Success Messages
```
📨 Received message from whatsapp:+1234567890: hello...
✅ Sent response (1 chunk(s))
```

### ⚠️ Warning Messages
```
⚠️ WARNING: Received POST request to / instead of /whatsapp
   Request data: {'From': '...', 'Body': '...'}
```

### ❌ Error Messages
```
❌ Error in whatsapp_webhook: [error details]
[Full traceback]
```

## Environment Variables Required

Make sure `.env` file has:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GEMINI_API_KEY=your_gemini_api_key (optional)
ANONYMIZATION_SALT=your_random_salt
PORT=5000
```

## Quick Checklist

Before testing:
- [ ] `.env` file exists with all required variables
- [ ] Bot starts without errors
- [ ] Health check returns 200
- [ ] ngrok is running (for local testing)
- [ ] Twilio webhook URL ends with `/whatsapp`
- [ ] Twilio webhook method is `POST`

## Still Having Issues?

1. Check bot console logs for error messages
2. Test each endpoint individually using curl
3. Verify Twilio webhook configuration
4. Check ngrok dashboard at `http://127.0.0.1:4040` for request details
5. Review Twilio Console → Monitor → Logs for webhook delivery status

