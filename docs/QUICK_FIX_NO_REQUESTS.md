# 🚨 QUICK FIX: No Requests Being Received

## Problem
You sent a Google Drive URL but **NO requests appear in the console**. This means Twilio can't reach your server.

## Root Cause
Your Flask server runs on `localhost:5000`, which is only accessible on your computer. Twilio needs a **publicly accessible URL**.

## ✅ IMMEDIATE SOLUTION

### Step 1: Install ngrok (if not installed)
```bash
# Download from https://ngrok.com/download
# Or use:
choco install ngrok  # Windows
```

### Step 2: Start ngrok in a NEW terminal
```bash
ngrok http 5000
```

**You'll see:**
```
Forwarding   https://abc123.ngrok.io -> http://localhost:5000
```

### Step 3: Copy the ngrok HTTPS URL
Copy the `https://abc123.ngrok.io` URL (yours will be different)

### Step 4: Configure Twilio Webhook

1. **Go to Twilio Console**: https://console.twilio.com
2. **Navigate to**: Phone Numbers → Manage → Active Numbers
3. **Click your WhatsApp number**
4. **Scroll to "Messaging" section**
5. **Set "A MESSAGE COMES IN" webhook:**
   - **URL**: `https://abc123.ngrok.io/whatsapp` (use YOUR ngrok URL)
   - **HTTP Method**: `POST`
6. **Click "Save"**

### Step 5: Test

1. **Send a message** to your WhatsApp bot
2. **Check the console** - you should NOW see:
   ```
   [DEBUG] ===== INCOMING REQUEST =====
   [DEBUG] Method: POST
   [DEBUG] Path: /whatsapp
   [DEBUG] Form data: {'From': '...', 'Body': '...'}
   ```

## 🔍 Verification

### Test 1: Check if server is running
```bash
curl http://localhost:5000/health
# Should return: {"status":"healthy","service":"mediguard-bot"}
```

### Test 2: Check if ngrok is working
```bash
curl https://your-ngrok-url.ngrok.io/health
# Should return: {"status":"healthy","service":"mediguard-bot"}
```

### Test 3: Check webhook endpoint
```bash
curl https://your-ngrok-url.ngrok.io/whatsapp
# Should return: "Webhook endpoint is active. Use POST for messages."
```

## 📋 Checklist

- [ ] Bot is running (`python mediguard_bot.py`)
- [ ] ngrok is running (`ngrok http 5000`)
- [ ] Copied ngrok HTTPS URL
- [ ] Set Twilio webhook to `https://your-ngrok-url.ngrok.io/whatsapp`
- [ ] Set webhook method to `POST`
- [ ] Saved Twilio configuration
- [ ] Sent test message
- [ ] Checked console for incoming requests

## 🎯 Expected Console Output

When a message is received, you'll see:
```
[DEBUG] ===== INCOMING REQUEST =====
[DEBUG] Method: POST
[DEBUG] Path: /whatsapp
[DEBUG] Form data: {'From': 'whatsapp:+1234567890', 'Body': 'https://drive.google.com/...', ...}
[DEBUG] WhatsApp Webhook Received
[DEBUG] Body: https://drive.google.com/...
[INFO] 🔗 Google Drive URL detected, converting to direct download...
```

## ⚠️ Important Notes

1. **ngrok URL changes** every time you restart ngrok (unless you have a paid account)
2. **Update Twilio webhook** if you restart ngrok
3. **Keep both running**: Bot AND ngrok must be running simultaneously
4. **Check Twilio Logs**: Twilio Console → Monitor → Logs → Messaging (shows webhook delivery attempts)

## 🚨 Still Not Working?

1. **Check ngrok web interface**: Open http://localhost:4040 in browser to see all requests
2. **Check Twilio Logs**: Look for webhook delivery errors
3. **Verify webhook URL**: Make sure it ends with `/whatsapp` (not `/`)
4. **Check firewall**: Make sure port 5000 isn't blocked

## ✅ Success Indicators

You'll know it's working when:
- ✅ Console shows `[DEBUG] ===== INCOMING REQUEST =====`
- ✅ Bot responds to messages
- ✅ Google Drive URLs are detected and processed
- ✅ Media uploads are detected

**The bot code is ready - you just need to configure the webhook!**

