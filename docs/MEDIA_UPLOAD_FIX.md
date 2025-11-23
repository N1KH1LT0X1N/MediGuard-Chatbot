# Media Upload Fix - PDF, Image, and Google Drive URLs

## Problem Identified

From the Twilio logs, the bot was receiving Google Drive URLs but returning generic "Error processing lab report" messages. The specific failures were:

1. **Google Drive URLs**: Not being properly converted to direct download links
2. **Error Messages**: Too generic, not showing actual failure points
3. **Authentication Issues**: Google Drive files requiring authentication not handled properly
4. **Large Files**: Google Drive virus scan warning for large files not handled

## Fixes Applied

### 1. Enhanced Google Drive URL Conversion

**File**: `mediguard/utils/media_handler.py`

**Changes**:
- Added support for multiple Google Drive URL formats:
  - `/file/d/ID/view` (standard share link)
  - `id=ID` (URL with id parameter)
  - `/open?id=ID` (open link format)
- Improved file ID extraction with better regex patterns
- Added logging for extracted file IDs

### 2. Google Drive Large File Handling

**Problem**: Google Drive shows a virus scan warning page for files > 100MB, which requires clicking "Download anyway"

**Solution**:
- Use a session to handle redirects
- Check for redirect status codes (302, 303, 307, 308)
- Follow redirects automatically
- Increased timeout to 60 seconds for large files
- Better User-Agent header to mimic browser

### 3. Improved Error Detection

**Changes**:
- Better detection of HTML error pages from Google Drive
- Specific error messages for authentication issues
- Clear instructions for users on how to fix sharing settings

**Error Messages Now Include**:
- "Google Drive file is not publicly accessible"
- Step-by-step instructions to fix sharing
- Specific guidance based on error type

### 4. Enhanced Error Logging

**File**: `mediguard_bot.py`

**Changes**:
- Added detailed error logging throughout media upload pipeline
- Log error types, URLs, and context
- Better audit logging for debugging
- Specific error messages based on failure point

**New Logging Includes**:
- Media URL being processed
- Error type and message
- File ID extraction results
- Redirect handling
- Download status

### 5. Better Error Messages for Users

**Before**:
```
Error processing lab report.
Please try:
- Send a clearer PDF/image
- Or use 'template' command to enter values manually
```

**After**:
```
Google Drive file is not publicly accessible.

To fix:
1. Right-click the file in Google Drive
2. Select 'Share' → 'Change to anyone with the link'
3. Set permission to 'Viewer'
4. Copy the new link and try again
```

## Testing

To test the fixes:

1. **Google Drive URL Test**:
   ```
   https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk
   ```

2. **Check Console Logs**:
   - Should see: `[DEBUG] Extracted Google Drive file ID: 1NUdDVck6Tv60JvLpojAVv22C8RD02kvf`
   - Should see: `[DEBUG] Attempting Google Drive direct download: ...`
   - Should see download progress or specific error

3. **Error Scenarios**:
   - Private file → Should get sharing instructions
   - Large file → Should handle redirect
   - Invalid URL → Should get clear error

## Next Steps

1. **Restart the bot** and test with the Google Drive URL from logs
2. **Monitor console** for detailed error messages
3. **Check Twilio logs** to see if responses are being sent
4. **Test with**:
   - Public Google Drive link
   - Private Google Drive link (should get helpful error)
   - Direct PDF URL
   - Image upload

## References

- [Twilio Webhook Documentation](https://www.twilio.com/docs/events/webhook-quickstart)
- [Twilio Error Logs](https://www.twilio.com/docs/events/event-types-list#error-logs)
- Google Drive sharing settings for public access

