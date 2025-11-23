# 📄 PDF Upload Workarounds for WhatsApp Bot

## Problem
Twilio WhatsApp API has limitations with direct PDF uploads:
- Users may not be able to attach PDFs directly in WhatsApp
- PDFs might not come through as media attachments
- WhatsApp may convert or reject PDF files

## ✅ Implemented Workarounds

### 1. **Image Upload (Primary Workaround)**
**How it works:**
- User takes a screenshot/photo of their lab report PDF
- Sends the image via WhatsApp
- Bot processes the image with OCR

**User Instructions:**
```
📸 Take a photo/screenshot of your lab report and send as image
```

**Advantages:**
- ✅ Works reliably in WhatsApp
- ✅ No conversion needed
- ✅ OCR works well on images
- ✅ Simple for users

### 2. **URL-Based Upload (Secondary Workaround)**
**How it works:**
- User uploads PDF to cloud storage (Google Drive, Dropbox, etc.)
- Gets a public shareable link
- Sends the URL in WhatsApp message
- Bot downloads and processes the PDF

**User Instructions:**
```
🔗 Send a public URL to your PDF (e.g., Google Drive share link)
```

**Implementation:**
- Detects URLs in messages using regex pattern
- Downloads from public URLs (no Twilio auth needed)
- Processes PDF normally

**Example:**
```
User: https://drive.google.com/file/d/abc123/lab_report.pdf
Bot: [Downloads and processes PDF]
```

### 3. **Enhanced Document Detection**
**How it works:**
- Checks for `MessageType` field (document vs media)
- Looks for `DocumentUrl`, `DocumentContentType`, `DocumentFilename`
- Handles PDFs that come through as document messages

**Implementation:**
- Enhanced `extract_media_from_twilio_request()` function
- Checks multiple field names for document messages
- Falls back to media message handling

### 4. **Better User Instructions**
**Updated Help Message:**
- Clear instructions on how to send lab reports
- Multiple options explained
- Prioritizes image upload (most reliable)

## Code Changes

### 1. Enhanced Media Detection (`mediguard/utils/media_handler.py`)
```python
def extract_media_from_twilio_request(request_form):
    # Checks for:
    # - MessageType (document vs media)
    # - DocumentUrl, DocumentContentType
    # - MediaUrl0, MediaContentType0
    # - Handles both document and media messages
```

### 2. URL Detection in Messages (`mediguard_bot.py`)
```python
# Detects URLs in text messages
url_pattern = r'https?://[^\s]+\.(pdf|jpg|jpeg|png|gif|bmp)'
if url_match:
    # Process as media upload
```

### 3. Public URL Download Support (`mediguard/utils/media_handler.py`)
```python
def download_media(media_url, account_sid, auth_token, ...):
    # Supports both:
    # - Twilio Media URLs (requires auth)
    # - Public URLs (no auth needed)
```

## User Experience

### Option 1: Image Upload (Recommended)
```
User: [Takes photo of lab report]
Bot: 📄 Lab report received! Processing with OCR...
Bot: [Extracts biomarkers and provides prediction]
```

### Option 2: URL Upload
```
User: https://drive.google.com/file/d/abc123/lab_report.pdf
Bot: 📄 Lab report received! Processing with OCR...
Bot: [Extracts biomarkers and provides prediction]
```

### Option 3: Manual Entry (Fallback)
```
User: template
Bot: [Shows JSON template]
User: { "hemoglobin": 14.5, ... }
Bot: [Processes and provides prediction]
```

## Testing

### Test Image Upload:
1. Take a screenshot of a lab report PDF
2. Send image via WhatsApp
3. Bot should detect and process

### Test URL Upload:
1. Upload PDF to Google Drive
2. Get shareable link (public access)
3. Send URL via WhatsApp
4. Bot should detect URL, download, and process

### Test Document Message:
1. Try sending PDF directly (if WhatsApp allows)
2. Check console logs for MessageType
3. Bot should detect and process

## Debugging

### Check Console Logs:
```
[DEBUG] MessageType: document
[DEBUG] MediaUrl0: https://...
[DEBUG] MediaContentType0: application/pdf
[INFO] ✅ Media detected! Type: application/pdf
```

### Common Issues:

1. **NumMedia = 0 but PDF sent**
   - Check for `DocumentUrl` or `MessageType: document`
   - May need to handle document messages differently

2. **URL not detected**
   - Ensure URL is in message body
   - Check regex pattern matches

3. **Download fails**
   - For public URLs: Check if URL is accessible
   - For Twilio URLs: Check authentication

## Next Steps

1. **Test with actual PDF uploads** to see what Twilio sends
2. **Refine document message handling** based on real data
3. **Add more cloud storage support** (Dropbox, OneDrive, etc.)
4. **Consider PDF to image conversion service** (if needed)

## Recommendations

**For Users:**
- ✅ **Best option:** Take screenshot/photo of lab report
- ✅ **Alternative:** Upload to Google Drive and share public link
- ✅ **Fallback:** Enter values manually using template

**For Developers:**
- Monitor console logs to see what Twilio actually sends
- Adjust detection logic based on real webhook data
- Consider adding PDF to image conversion if needed

