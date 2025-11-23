# 🚀 How to Start the Bot (Complete Guide)

## Current Status
✅ Bot code is ready and running
✅ All media detection is implemented
✅ Google Drive URL support is ready
❌ **Webhook not configured** (that's why no requests are received)

## Step-by-Step Setup

### 1. Start the Bot
```bash
python mediguard_bot.py
```

**You should see:**
```
🚀 MediGuard AI Bot starting on port 5000...
📋 WEBHOOK CONFIGURATION REQUIRED:
   1. For local testing, use ngrok:
      ngrok http 5000
   ...
```

### 2. Start ngrok (in a NEW terminal)
```bash
ngrok http 5000
```

**You'll see:**
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

### 3. Configure Twilio Webhook

**In Twilio Console:**
1. Go to: Phone Numbers → Manage → Active Numbers
2. Click your WhatsApp number
3. Under "Messaging" → "A MESSAGE COMES IN":
   - **URL**: `https://abc123.ngrok.io/whatsapp` (use YOUR ngrok URL)
   - **HTTP Method**: `POST`
4. **Save**

### 4. Test

Send a message to your WhatsApp bot. You should see in console:
```
[DEBUG] ===== INCOMING REQUEST =====
[DEBUG] Method: POST
[DEBUG] Path: /whatsapp
[DEBUG] Form data: {...}
```

## What Works Now

✅ **Image uploads** - Detected via MediaUrl0
✅ **PDF uploads** - Detected via MediaUrl0 or DocumentUrl
✅ **Google Drive URLs** - Detected in message body, converted to direct download
✅ **Other URLs** - Detected and processed
✅ **Comprehensive logging** - Shows ALL incoming requests

## Troubleshooting

### No requests in console?
→ **Webhook not configured** - Follow steps above

### 404 Not Found?
→ **Wrong webhook URL** - Make sure it ends with `/whatsapp`

### 405 Method Not Allowed?
→ **Wrong HTTP method** - Set to `POST` in Twilio

### ngrok URL changed?
→ **Update Twilio webhook** with new ngrok URL

## Next Steps

1. ✅ Set up ngrok
2. ✅ Configure Twilio webhook
3. ✅ Test with a message
4. ✅ Check console logs
5. ✅ Send Google Drive URL
6. ✅ Verify it's processed

**The code is ready - you just need to expose the server!**

