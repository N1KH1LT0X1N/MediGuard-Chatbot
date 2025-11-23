# 🔍 Media Upload Debugging Guide

## Issue
User uploaded a PDF to WhatsApp bot but received no output.

## Debugging Steps Added

### 1. Enhanced Webhook Logging
- Logs all incoming request data (NumMedia, MediaUrl0, MediaContentType0)
- Shows all form keys to identify missing fields
- Tracks media detection flow

### 2. Media Extraction Debugging
- Logs NumMedia value parsing
- Shows MediaUrl0, MediaContentType0, MediaSid0 values
- Indicates when media is detected or missing

### 3. Media Upload Handler Debugging
- Logs entry into handle_media_upload
- Tracks media URL and content type
- Shows download progress and results
- Logs file validation steps
- Tracks OCR processing flow
- Shows biomarker extraction results
- Logs all exceptions with full tracebacks

## How to Debug

### Step 1: Check Console Output
When a PDF is uploaded, you should see:
```
[DEBUG] ============================================================
[DEBUG] WhatsApp Webhook Received
[DEBUG] User ID: whatsapp:+1234567890
[DEBUG] Body: (empty)
[DEBUG] NumMedia: 1
[DEBUG] MediaUrl0: https://...
[DEBUG] MediaContentType0: application/pdf
[DEBUG] All form keys: ['From', 'NumMedia', 'MediaUrl0', ...]
[DEBUG] ============================================================
```

### Step 2: Check Media Detection
Look for:
```
[DEBUG] extract_media_from_twilio_request: NumMedia=1
[DEBUG] MediaUrl0: https://...
[INFO] ✅ Media detected! Type: application/pdf
```

### Step 3: Check Download
Look for:
```
[INFO] Downloading media from Twilio...
[DEBUG] Using Account SID: AC...
[DEBUG] File extension: .pdf
[DEBUG] Download result - File path: C:\..., Error: None
✅ Downloaded media: lab_report_abc123.pdf (250.50KB)
```

### Step 4: Check OCR Processing
Look for:
```
[INFO] Extracting text from lab report: lab_report_abc123.pdf
[INFO] Attempting Gemini Vision extraction...
[OK] OCR extraction successful (gemini): 1234 characters
```

## Common Issues

### Issue 1: NumMedia = 0
**Symptom:** `[DEBUG] No media detected (NumMedia=0)`
**Cause:** Twilio webhook not configured correctly or media not attached
**Solution:** Check Twilio webhook configuration

### Issue 2: MediaUrl0 Missing
**Symptom:** `[DEBUG] MediaUrl0 is missing, returning None`
**Cause:** Twilio didn't send media URL
**Solution:** Check Twilio account settings, ensure media is enabled

### Issue 3: Download Fails
**Symptom:** `[ERROR] Media download failed: ...`
**Cause:** Authentication issue or network problem
**Solution:** Check TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN

### Issue 4: OCR Fails Silently
**Symptom:** No error but no response
**Cause:** Exception caught but not logged properly
**Solution:** Check full traceback in console

### Issue 5: Response Not Sent
**Symptom:** Processing completes but user gets no message
**Cause:** TwiML response format issue
**Solution:** Check response format, ensure MessagingResponse is used correctly

## Testing

1. **Restart the bot** to load new debugging code
2. **Upload a PDF** via WhatsApp
3. **Check console output** for debug messages
4. **Identify the failure point** from logs
5. **Fix the specific issue**

## Next Steps

After identifying the issue from debug logs:
1. Fix the specific problem
2. Test again
3. Remove excessive debug logging (keep essential logs)
4. Document the fix

