# Google Drive URL Fix - Complete Solution

## Problem Analysis

From the logs (line 2-8 of CSV):
- User sent: `https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk`
- Bot responded: "Error processing lab report: Could not read text from image"

**Root Cause**: The error "Could not read text from image" indicates OCR extraction failed. This happens when:
1. File downloads as HTML (Google Drive error page) instead of PDF
2. File is corrupted during download
3. OCR service fails

## Flow Analysis

**Current Flow:**
1. User sends Google Drive URL → Twilio receives it
2. `handle_message()` detects Google Drive URL in message body
3. Converts to direct download URL: `https://drive.google.com/uc?export=download&id=FILE_ID`
4. Calls `handle_media_upload()` with converted URL
5. `download_media()` receives URL and tries to convert again (double conversion issue)
6. Downloads file
7. Validates file
8. OCR extraction
9. Biomarker extraction
10. Prediction

## Issues Fixed

### 1. **Double URL Conversion**
- **Problem**: `handle_message()` converts URL, then `download_media()` tries to convert again
- **Fix**: Pass original URL to `download_media()`, let it handle conversion internally
- **File**: `mediguard_bot.py` (line 336-357)

### 2. **Better Logging**
- Added comprehensive logging at each step:
  - Google Drive URL detection
  - File ID extraction
  - URL conversion
  - Download status
  - File validation
  - OCR extraction
- **Files**: `mediguard_bot.py`, `mediguard/utils/media_handler.py`

### 3. **Enhanced Error Detection**
- Check downloaded file size
- Verify file is not HTML before OCR
- Better error messages for each failure point
- **File**: `mediguard/utils/media_handler.py` (line 211-255)

### 4. **OCR Error Handling**
- More specific error messages based on failure type
- Log file path, size, and first bytes for debugging
- **File**: `mediguard_bot.py` (line 750-867)

## Key Changes

### `mediguard_bot.py`:
```python
# Before: Converted URL in handle_message()
direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
fake_media_info = {"media_url": direct_url, ...}

# After: Pass original URL, let download_media() convert it
fake_media_info = {"media_url": original_url, ...}
```

### `mediguard/utils/media_handler.py`:
- Enhanced Google Drive URL conversion with better logging
- Check file size after download
- Verify file is not HTML before proceeding
- Better error messages for each failure type

## Testing

To test the fix:

1. **Send Google Drive URL**:
   ```
   https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk
   ```

2. **Check console logs** for:
   ```
   [INFO] ========== GOOGLE DRIVE URL DETECTED ==========
   [INFO] Original URL: https://drive.google.com/...
   [INFO] Extracted File ID: 1NUdDVck6Tv60JvLpojAVv22C8RD02kvf
   [DEBUG] ========== GOOGLE DRIVE URL CONVERSION ==========
   [DEBUG] Converted to direct download URL: ...
   [DEBUG] Downloaded file size: X bytes
   [DEBUG] ========== STARTING OCR EXTRACTION ==========
   ```

3. **Expected behavior**:
   - URL detected and converted correctly
   - File downloads successfully
   - File is validated (not HTML)
   - OCR extraction succeeds
   - Biomarkers extracted
   - Prediction returned

## Common Issues & Solutions

### Issue: "Could not read text from image"
**Possible causes:**
1. File is HTML (Google Drive error page) → Check sharing settings
2. File is corrupted → Re-download
3. OCR service unavailable → Check API keys

**Solution**: Check console logs for file size and first bytes. If HTML detected, user needs to share file publicly.

### Issue: "Google Drive file is not publicly accessible"
**Solution**: 
1. Right-click file in Google Drive
2. Click "Share" → "Change to anyone with the link"
3. Set permission to "Viewer"
4. Copy new link and try again

### Issue: "File too large or requires virus scan confirmation"
**Solution**: For files > 100MB, Google Drive shows virus scan warning. User needs to:
1. Download manually first to confirm it works
2. Or convert PDF to images and send those instead

## Next Steps

1. **Test with actual Google Drive URL** from logs
2. **Monitor console output** for detailed logs
3. **Verify each step** completes successfully
4. **Check error messages** are specific and helpful

## Files Modified

1. `mediguard_bot.py`:
   - Pass original Google Drive URL to download handler
   - Enhanced OCR error logging
   - Better error messages

2. `mediguard/utils/media_handler.py`:
   - Enhanced Google Drive URL conversion logging
   - Better file validation (check for HTML)
   - Improved error detection and messages

