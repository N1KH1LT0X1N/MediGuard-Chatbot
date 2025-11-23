# Complete Media Upload Fix - PDF, Image, and Google Drive URLs

## Problem Analysis from Logs

**From `sms-log-AC1218c9122ea2718d466fe5c7255afb39_2025-11-23 (1).csv`:**

1. **Google Drive URLs** (lines 7, 13):
   - User sent: `https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk`
   - Bot responded: "Error processing lab report"
   - **Status**: Failed

2. **Empty Messages with ErrorCode 11200** (lines 14-15):
   - Body: "" (empty)
   - ErrorCode: 11200 (HTTP retrieval failure)
   - **Status**: These are likely PDF/image uploads that Twilio couldn't retrieve

3. **Text Messages** (hello, help, template):
   - **Status**: Working correctly ✅

## Root Causes

### 1. ErrorCode 11200 Not Handled
- **ErrorCode 11200** = "HTTP retrieval failure" - Twilio couldn't fetch the media
- When this happens, `Body` is empty but media URL might still be in request
- Bot wasn't checking for media when Body was empty

### 2. Google Drive URL Conversion Issues
- Google Drive share links need proper conversion to direct download
- Large files show virus scan warning page (HTML) instead of file
- Need to handle redirects and extract download links from warning pages

### 3. Generic Error Messages
- All failures returned same generic message
- Users couldn't tell what went wrong
- No guidance on how to fix

## Fixes Applied

### 1. ErrorCode 11200 Handling

**File**: `mediguard_bot.py`

**Changes**:
- Detect ErrorCode 11200 in webhook
- Still attempt to extract media (URL might be available)
- Provide specific error message if media truly unavailable
- Log error code for debugging

```python
error_code = request.form.get("ErrorCode", "")
if error_code == "11200":
    # Still try to extract media - sometimes URL is available
    # Provide helpful error if media truly unavailable
```

### 2. Enhanced Google Drive Handling

**File**: `mediguard/utils/media_handler.py`

**Improvements**:
- Better file ID extraction (handles multiple URL formats)
- Handle virus scan warning pages for large files
- Extract download link from HTML warning page
- Better error detection (sign-in required, access denied, etc.)
- Specific error messages for each failure type

**New Features**:
- Detects virus scan warning pages
- Extracts actual download link from HTML
- Handles redirects properly
- Longer timeout for large files (60s)

### 3. Improved Error Messages

**Before**:
```
Error processing lab report.
Please try:
- Send a clearer PDF/image
- Or use 'template' command to enter values manually
```

**After** (Google Drive not accessible):
```
Google Drive file is not publicly accessible.

To fix:
1. Right-click the file in Google Drive
2. Select 'Share' → 'Change to anyone with the link'
3. Set permission to 'Viewer'
4. Copy the new link and try again
```

**After** (ErrorCode 11200):
```
I received your media upload, but Twilio couldn't retrieve it.

Please try:
- For PDFs: Send as image instead, or share via Google Drive link
- For images: Ensure file is under 10MB and in JPG/PNG format
- Or use 'template' command to enter values manually
```

### 4. Better Media Detection

**Improvements**:
- Check for media even when Body is empty (ErrorCode 11200 case)
- Log ErrorCode for debugging
- Check all possible Twilio fields for media URLs
- Handle document messages properly

## Testing Checklist

### ✅ Test Cases

1. **Google Drive URL (Public)**:
   - Send: `https://drive.google.com/file/d/ID/view`
   - Expected: Should download and process

2. **Google Drive URL (Private)**:
   - Send: Private Google Drive link
   - Expected: Should get sharing instructions

3. **PDF Upload via Twilio**:
   - Upload PDF directly
   - Expected: Should process or get helpful error

4. **Image Upload via Twilio**:
   - Upload image directly
   - Expected: Should process

5. **ErrorCode 11200**:
   - If Twilio can't retrieve media
   - Expected: Should get helpful error message

## Debugging

When testing, check console logs for:

1. **ErrorCode detection**:
   ```
   [WARN] Twilio ErrorCode detected: 11200
   ```

2. **Google Drive conversion**:
   ```
   [DEBUG] Extracted Google Drive file ID: 1NUdDVck6Tv60JvLpojAVv22C8RD02kvf
   [DEBUG] Attempting Google Drive direct download: ...
   ```

3. **Download status**:
   ```
   [OK] Downloaded media: lab_report_xxx.pdf (123.45KB)
   ```

4. **Error details**:
   ```
   [ERROR] Media download failed: Google Drive file is not publicly accessible...
   ```

## Next Steps

1. **Restart the bot**:
   ```bash
   python mediguard_bot.py
   ```

2. **Test with Google Drive URL from logs**:
   - URL: `https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk`
   - Check console for detailed logs
   - Should see file ID extraction and download attempt

3. **If still failing**:
   - Check if file is publicly shared
   - Verify file size (should be < 10MB)
   - Check console logs for specific error

## Files Modified

1. **`mediguard_bot.py`**:
   - Added ErrorCode 11200 detection
   - Improved media detection when Body is empty
   - Better error messages for media failures

2. **`mediguard/utils/media_handler.py`**:
   - Enhanced Google Drive URL conversion
   - Handle virus scan warning pages
   - Extract download links from HTML
   - Better error detection and messages

## References

- [Twilio Error 11200](https://www.twilio.com/docs/api/errors/11200)
- [Twilio Webhook Documentation](https://www.twilio.com/docs/events/webhook-quickstart)
- [Twilio Error Logs](https://www.twilio.com/docs/events/event-types-list#error-logs)

