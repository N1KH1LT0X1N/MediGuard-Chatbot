# 🔧 Webhook Setup Guide - Fix "No Requests Received"

## Problem
When you send a message/URL to WhatsApp bot, **NO requests appear in the console**. This means Twilio isn't reaching your server.

## Root Cause
Your Flask server is running locally (`localhost:5000`), but Twilio needs a **publicly accessible URL** to send webhooks.

## ✅ Solution: Use ngrok (for Local Development)

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or use package manager
choco install ngrok  # Windows
brew install ngrok   # macOS
```

### Step 2: Start Your Bot
```bash
python mediguard_bot.py
```

You should see:
```
🚀 MediGuard AI Bot starting on port 5000...
```

### Step 3: Start ngrok
```bash
ngrok http 5000
```

You'll see output like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

### Step 4: Configure Twilio Webhook

1. **Copy the ngrok HTTPS URL** (e.g., `https://abc123.ngrok.io`)
2. **Go to Twilio Console** → Phone Numbers → Manage → Active Numbers
3. **Select your WhatsApp number**
4. **Under "Messaging" section**, set:
   - **Webhook URL**: `https://abc123.ngrok.io/whatsapp`
   - **HTTP Method**: `POST`
5. **Save**

### Step 5: Test

1. **Send a message** to your WhatsApp bot
2. **Check console** - you should now see:
   ```
   [DEBUG] ===== INCOMING REQUEST =====
   [DEBUG] Method: POST
   [DEBUG] Path: /whatsapp
   ```

## 🔍 Verification Steps

### Test 1: Check if server is accessible
```bash
curl http://localhost:5000/health
# Should return: {"status":"healthy","service":"mediguard-bot"}
```

### Test 2: Check if ngrok is forwarding
```bash
curl https://your-ngrok-url.ngrok.io/health
# Should return: {"status":"healthy","service":"mediguard-bot"}
```

### Test 3: Check webhook endpoint
```bash
curl https://your-ngrok-url.ngrok.io/whatsapp
# Should return: "Webhook endpoint is active. Use POST for messages."
```

## 🚨 Common Issues

### Issue 1: ngrok URL changes on restart
**Solution:** Use ngrok with a static domain (requires ngrok account):
```bash
ngrok http 5000 --domain=your-static-domain.ngrok.io
```

### Issue 2: Still no requests after setup
**Check:**
1. ✅ ngrok is running
2. ✅ Bot is running on port 5000
3. ✅ Twilio webhook URL is set correctly
4. ✅ Webhook method is POST (not GET)
5. ✅ WhatsApp number is active in Twilio

### Issue 3: 404 Not Found
**Solution:** Make sure webhook URL ends with `/whatsapp` (not just `/`)

### Issue 4: 405 Method Not Allowed
**Solution:** Make sure webhook method is set to `POST` in Twilio

## 📋 Quick Checklist

- [ ] Bot is running (`python mediguard_bot.py`)
- [ ] ngrok is running (`ngrok http 5000`)
- [ ] Copied ngrok HTTPS URL
- [ ] Set Twilio webhook to `https://your-ngrok-url.ngrok.io/whatsapp`
- [ ] Set webhook method to `POST`
- [ ] Saved Twilio configuration
- [ ] Sent test message
- [ ] Checked console for incoming requests

## 🎯 Expected Console Output

When a message is received, you should see:
```
[DEBUG] ===== INCOMING REQUEST =====
[DEBUG] Method: POST
[DEBUG] Path: /whatsapp
[DEBUG] Form data: {'From': 'whatsapp:+1234567890', 'Body': '...', ...}
[DEBUG] WhatsApp Webhook Received
[DEBUG] User ID: whatsapp:+1234567890
[DEBUG] Body: https://drive.google.com/...
```

## 🔄 For Production

Instead of ngrok, use:
- **Heroku** (free tier available)
- **Railway** (free tier)
- **Render** (free tier)
- **AWS/GCP/Azure** (paid)

Set webhook URL to: `https://your-domain.com/whatsapp`

## 📞 Still Not Working?

1. **Check Twilio Logs:**
   - Twilio Console → Monitor → Logs → Messaging
   - Look for webhook delivery attempts
   - Check for error codes

2. **Check ngrok Web Interface:**
   - Open http://localhost:4040 in browser
   - See all requests going through ngrok

3. **Test with curl:**
   ```bash
   curl -X POST https://your-ngrok-url.ngrok.io/whatsapp \
     -d "From=whatsapp:+1234567890" \
     -d "Body=test message"
   ```

4. **Check Firewall:**
   - Make sure port 5000 isn't blocked
   - Windows Firewall might need to allow Python

## ✅ Success Indicators

You'll know it's working when:
- ✅ Console shows incoming requests
- ✅ Bot responds to messages
- ✅ Media uploads are detected
- ✅ URLs in messages are processed

