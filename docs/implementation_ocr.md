# 📄 PDF Lab Report OCR Implementation Plan
## MediGuard AI - Automated Biomarker Extraction from PDF/Image Lab Reports

---

## 🎯 Objective

Enable users to upload PDF or image lab reports via WhatsApp, automatically extract biomarker values using OCR, and process them through the existing MediGuard prediction pipeline.

**User Experience:**
- User sends PDF/image of lab report via WhatsApp
- Bot extracts all 24 biomarker values automatically
- Bot processes and returns prediction (same as manual JSON input)

---

## 📋 Implementation Overview

### Architecture
```
WhatsApp Media Upload → PDF/Image Processing → OCR Extraction → 
Biomarker Parsing → Existing Prediction Pipeline
```

### Key Components
1. **Media Handler** - Receive PDF/image from Twilio
2. **OCR Engine** - Extract text from PDF/image (hybrid: LLM + Tesseract)
3. **Biomarker Parser** - Extract 24 biomarker values from OCR text
4. **Integration** - Connect to existing `BiomarkerInputParser`

---

## 🏗️ Step-by-Step Implementation

### Phase 1: Media Handling & File Processing

#### 1.1 Add Media Handling to `mediguard_bot.py`

**Location:** `mediguard_bot.py` - `whatsapp_webhook()` function

**Changes:**
- Check for media attachments in Twilio webhook
- Download PDF/image files from Twilio Media URLs
- Save temporarily to disk
- Route to OCR processing

**Code Structure:**
```python
@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    # Existing code...
    
    # Check for media attachments
    num_media = int(request.form.get("NumMedia", "0"))
    if num_media > 0:
        # Handle media upload
        return handle_media_upload(user_id, request)
    
    # Existing text message handling...
```

#### 1.2 Create Media Handler Module

**New File:** `mediguard/utils/media_handler.py`

**Functions:**
- `download_media(url, file_path)` - Download from Twilio Media URL
- `is_valid_lab_report(file_path)` - Validate file type (PDF/image)
- `cleanup_temp_file(file_path)` - Remove temporary files

**Dependencies:**
- `requests` - Download media
- `pathlib` - File handling
- `tempfile` - Temporary file management

---

### Phase 2: OCR Engine (Hybrid Approach)

#### 2.1 Create OCR Module

**New File:** `mediguard/parsers/lab_report_ocr.py`

**Class:** `LabReportOCR`

**Methods:**
- `extract_text(file_path)` - Extract text from PDF/image
- `extract_with_llm(file_path)` - Use Gemini/OpenAI for extraction (primary)
- `extract_with_tesseract(file_path)` - Use Tesseract OCR (fallback)
- `convert_pdf_to_image(pdf_path)` - Convert PDF to image for OCR

**Hybrid Logic:**
```python
def extract_text(self, file_path):
    # Try LLM first (if API key available)
    if self.llm_available:
        try:
            return self.extract_with_llm(file_path)
        except Exception as e:
            print(f"LLM extraction failed: {e}, falling back to Tesseract")
    
    # Fallback to Tesseract
    return self.extract_with_tesseract(file_path)
```

#### 2.2 LLM-Based Extraction (Primary Method)

**Using Gemini API** (already configured in bot)

**Approach:**
- Send PDF/image to Gemini Vision API
- Use structured prompt to extract biomarker values
- Return JSON with all 24 biomarkers

**Prompt Template:**
```
Extract all biomarker values from this lab report. Return JSON with:
{
  "hemoglobin": <value>,
  "wbc_count": <value>,
  "platelet_count": <value>,
  ...
}

If a biomarker is not found, use null. Use standard units.
```

**Advantages:**
- High accuracy (90%+)
- Handles various lab report formats
- Understands context and units
- Already have Gemini API key configured

#### 2.3 Tesseract OCR (Fallback Method)

**For offline/backup scenarios**

**Process:**
1. Convert PDF to image (if needed)
2. Run Tesseract OCR
3. Extract text
4. Parse using regex patterns

**Dependencies:**
- `pytesseract` - Python wrapper for Tesseract
- `pdf2image` - PDF to image conversion
- `Pillow` - Image processing

---

### Phase 3: Biomarker Extraction from OCR Text

#### 3.1 Create Biomarker Extractor

**New File:** `mediguard/parsers/biomarker_extractor.py`

**Class:** `BiomarkerExtractor`

**Methods:**
- `extract_from_text(ocr_text)` - Main extraction method
- `extract_with_llm(ocr_text)` - Use LLM to parse text → JSON
- `extract_with_regex(ocr_text)` - Regex-based parsing (fallback)
- `normalize_biomarker_name(text)` - Map variations to standard names
- `parse_value(text, unit)` - Extract numeric value with unit conversion

**Biomarker Name Variations:**
- Hemoglobin: HGB, Hb, Hemo, Hemoglobin
- WBC: White Blood Cell, WBC Count, Leukocyte Count
- Platelet: PLT, Platelet Count, Thrombocyte
- etc. (use existing aliases from `BiomarkerInputParser`)

#### 3.2 LLM-Based Parsing (Primary)

**Using Gemini to parse OCR text:**

**Prompt:**
```
Parse this lab report text and extract biomarker values. 
Return JSON with all 24 biomarkers:
- hemoglobin (HGB, Hb)
- wbc_count (WBC, White Blood Cell)
- platelet_count (PLT, Platelet)
- glucose (GLU, Blood Sugar)
- creatinine (CREAT, Cr)
- bun (BUN, Blood Urea Nitrogen)
- sodium (Na)
- potassium (K)
- chloride (Cl)
- calcium (Ca)
- alt (ALT, Alanine Aminotransferase)
- ast (AST, Aspartate Aminotransferase)
- bilirubin_total (TBIL, Total Bilirubin)
- albumin (ALB)
- total_protein (TP, Protein)
- ldh (LDH, Lactate Dehydrogenase)
- troponin (TnI, Troponin I)
- bnp (BNP, B-Type Natriuretic Peptide)
- crp (CRP, C-Reactive Protein)
- esr (ESR, Erythrocyte Sedimentation Rate)
- procalcitonin (PCT)
- d_dimer (DD, D-Dimer)
- inr (INR, International Normalized Ratio)
- lactate (LAC, Lactate)

Text: {ocr_text}

Return only valid JSON, use null for missing values.
```

#### 3.3 Regex-Based Parsing (Fallback)

**Pattern Matching Strategy:**

1. **Find biomarker names** (with aliases)
2. **Extract adjacent values** (numbers with units)
3. **Normalize units** (convert to standard units)
4. **Validate ranges** (check if values are reasonable)

**Example Pattern:**
```python
# Pattern: "Hemoglobin" or "HGB" followed by number and unit
pattern = r'(?:hemoglobin|hgb|hb)\s*[:=]?\s*(\d+\.?\d*)\s*(?:g/dl|g/dL|gm%)'
```

**Challenges:**
- Lab reports have varied formats
- Units may vary (mg/dL vs g/dL)
- Some biomarkers may be missing
- Need to handle tables vs. free text

---

### Phase 4: Integration with Existing Parser

#### 4.1 Extend `BiomarkerInputParser`

**File:** `mediguard/parsers/input_parser.py`

**New Method:**
```python
def parse_from_ocr(self, ocr_text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
    """
    Parse biomarker values from OCR-extracted text.
    
    Args:
        ocr_text: Text extracted from lab report PDF/image
        
    Returns:
        Tuple of (parsed_values_dict, error_messages)
    """
    # Use BiomarkerExtractor to extract values
    # Return in same format as existing parse() method
```

#### 4.2 Update Message Handler

**File:** `mediguard_bot.py`

**Modify `handle_message()` to:**
- Check if message is media upload
- Route to OCR processing
- Use existing prediction pipeline

---

### Phase 5: Error Handling & User Feedback

#### 5.1 Error Scenarios

1. **Invalid file type** - Not PDF/image
2. **OCR extraction fails** - No text extracted
3. **Biomarker extraction fails** - Can't find values
4. **Missing biomarkers** - Some values not found
5. **Invalid values** - Values out of range

#### 5.2 User Feedback Messages

```python
# Success
"✅ Lab report processed! Found {count}/24 biomarkers. Processing prediction..."

# Partial success
"⚠️ Found {count}/24 biomarkers. Some values may be missing. Processing with available data..."

# Failure
"❌ Could not extract biomarker values from the lab report. Please try:\n• Send a clearer image\n• Or manually enter values using 'template' command"
```

---

## 📦 Dependencies to Add

### Update `requirements.txt`:

```txt
# OCR Dependencies
pytesseract>=0.3.10
Pillow>=10.0.0
pdf2image>=1.16.0

# Media Handling
requests>=2.31.0

# Optional: For better LLM extraction
# google-generativeai>=0.3.0  # Already installed
```

### System Dependencies:

**Tesseract OCR** (for fallback):
- **Windows:** Download from https://github.com/UB-Mannheim/tesseract/wiki
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt-get install tesseract-ocr`

**poppler** (for PDF conversion):
- **Windows:** Download from https://github.com/oschwartz10612/poppler-windows/releases
- **macOS:** `brew install poppler`
- **Linux:** `sudo apt-get install poppler-utils`

---

## 🗂️ File Structure

```
mediguard/
├── parsers/
│   ├── __init__.py
│   ├── input_parser.py          # Existing (extend)
│   ├── lab_report_ocr.py        # NEW: OCR engine
│   └── biomarker_extractor.py   # NEW: Extract biomarkers from text
├── utils/
│   ├── __init__.py
│   ├── formatters.py            # Existing
│   ├── security.py              # Existing
│   └── media_handler.py         # NEW: Handle media uploads
└── ...
```

---

## 🔄 Processing Flow

### Complete Flow Diagram:

```
1. User sends PDF/image via WhatsApp
   ↓
2. Twilio webhook receives media URL
   ↓
3. media_handler.py downloads file
   ↓
4. lab_report_ocr.py extracts text
   ├─→ Try LLM (Gemini Vision) → Extract structured JSON
   └─→ Fallback: Tesseract OCR → Extract raw text
   ↓
5. biomarker_extractor.py parses text
   ├─→ Try LLM parsing → Get biomarker dict
   └─→ Fallback: Regex parsing → Extract values
   ↓
6. BiomarkerInputParser validates & normalizes
   ↓
7. Existing prediction pipeline
   ├─→ BiomarkerScaler
   ├─→ MediGuardPredictor
   └─→ MedicalRAGEngine
   ↓
8. Format response & send to user
```

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tests/test_lab_report_ocr.py`

**Test Cases:**
1. PDF to image conversion
2. OCR text extraction (Tesseract)
3. LLM text extraction (mock)
4. Biomarker extraction from sample text
5. Integration with existing parser
6. Error handling (invalid files, missing biomarkers)

### Integration Tests

**Test Scenarios:**
1. Send sample lab report PDF via WhatsApp
2. Verify all 24 biomarkers extracted
3. Verify prediction generated correctly
4. Test with partial data (some biomarkers missing)
5. Test with poor quality image (fallback to regex)

### Sample Test Data

Create sample lab reports:
- `tests/samples/lab_report_complete.pdf` - All biomarkers
- `tests/samples/lab_report_partial.pdf` - Some missing
- `tests/samples/lab_report_poor_quality.jpg` - Low resolution

---

## 🚀 Implementation Steps (Ordered)

### Step 1: Setup Dependencies
- [ ] Add OCR dependencies to `requirements.txt`
- [ ] Install Tesseract OCR system package
- [ ] Install poppler (for PDF conversion)
- [ ] Test installations

### Step 2: Media Handler
- [ ] Create `mediguard/utils/media_handler.py`
- [ ] Implement file download from Twilio
- [ ] Add file validation
- [ ] Add cleanup functions
- [ ] Test with sample media URLs

### Step 3: OCR Engine
- [ ] Create `mediguard/parsers/lab_report_ocr.py`
- [ ] Implement PDF to image conversion
- [ ] Implement Tesseract OCR extraction
- [ ] Implement LLM extraction (Gemini Vision)
- [ ] Add hybrid fallback logic
- [ ] Test with sample PDFs/images

### Step 4: Biomarker Extractor
- [ ] Create `mediguard/parsers/biomarker_extractor.py`
- [ ] Implement LLM-based parsing
- [ ] Implement regex-based parsing
- [ ] Add unit normalization
- [ ] Add biomarker name aliases
- [ ] Test with sample OCR text

### Step 5: Integration
- [ ] Extend `BiomarkerInputParser` with `parse_from_ocr()`
- [ ] Update `mediguard_bot.py` to handle media
- [ ] Add user feedback messages
- [ ] Add error handling
- [ ] Test end-to-end flow

### Step 6: Testing & Refinement
- [ ] Write unit tests
- [ ] Test with various lab report formats
- [ ] Test error scenarios
- [ ] Optimize extraction accuracy
- [ ] Add logging and monitoring

---

## 🎨 User Experience Flow

### Happy Path:
```
User: [Sends PDF lab report]
Bot: "📄 Processing lab report... Please wait."
     [OCR extraction...]
     "✅ Found 24/24 biomarkers. Analyzing..."
     [Prediction...]
     "🚨 MediGuard AI Prediction
      Prediction: Sepsis
      Confidence: 87.5%
      ..."
```

### Partial Success:
```
User: [Sends PDF lab report]
Bot: "📄 Processing lab report..."
     "⚠️ Found 18/24 biomarkers. Some values may be missing."
     "Processing with available data..."
     [Prediction with available biomarkers]
```

### Error Case:
```
User: [Sends PDF lab report]
Bot: "📄 Processing lab report..."
     "❌ Could not extract biomarker values. Please try:"
     "• Send a clearer image/PDF"
     "• Or use 'template' command to enter values manually"
```

---

## 🔒 Security & Privacy Considerations

1. **Temporary File Storage**
   - Store files in secure temp directory
   - Auto-delete after processing
   - Set proper file permissions

2. **PHI Protection**
   - Don't log raw OCR text
   - Anonymize file paths in logs
   - Use existing `SecureLogger` for audit trail

3. **File Size Limits**
   - Limit PDF/image size (e.g., 10MB)
   - Reject suspicious file types
   - Timeout for long processing

4. **Rate Limiting**
   - Limit media uploads per user
   - Prevent abuse

---

## 📊 Success Metrics

- **Extraction Accuracy:** >85% of biomarkers correctly extracted
- **Processing Time:** <10 seconds for PDF/image
- **User Satisfaction:** Users prefer PDF upload over manual entry
- **Error Rate:** <10% complete failures

---

## 🐛 Known Challenges & Solutions

### Challenge 1: Varied Lab Report Formats
**Solution:** Use LLM (Gemini) which understands context and can adapt to different formats

### Challenge 2: Unit Conversion
**Solution:** Maintain unit conversion table, normalize all values to standard units

### Challenge 3: Missing Biomarkers
**Solution:** 
- Allow partial extraction (process with available biomarkers)
- Use default values for missing (with warning)
- Ask user to confirm missing values

### Challenge 4: Poor Image Quality
**Solution:**
- Pre-process images (enhance contrast, denoise)
- Use high-quality OCR settings
- Fallback to manual entry prompt

### Challenge 5: Cost of LLM API Calls
**Solution:**
- Use Gemini (free tier available)
- Cache results for duplicate files
- Fallback to Tesseract for offline scenarios

---

## 🔮 Future Enhancements

1. **Multi-page PDF support** - Handle lab reports with multiple pages
2. **Table detection** - Better extraction from tabular formats
3. **Handwriting recognition** - Support handwritten lab reports
4. **Batch processing** - Process multiple reports at once
5. **Confidence scoring** - Report extraction confidence per biomarker
6. **User correction** - Allow users to correct extracted values
7. **Format learning** - Learn from user corrections to improve accuracy

---

## 📝 Implementation Checklist

### Phase 1: Foundation
- [ ] Add dependencies to requirements.txt
- [ ] Install system dependencies (Tesseract, poppler)
- [ ] Create media_handler.py
- [ ] Test media download from Twilio

### Phase 2: OCR Engine
- [ ] Create lab_report_ocr.py
- [ ] Implement PDF to image conversion
- [ ] Implement Tesseract OCR
- [ ] Implement Gemini Vision API integration
- [ ] Test OCR extraction

### Phase 3: Biomarker Extraction
- [ ] Create biomarker_extractor.py
- [ ] Implement LLM-based parsing
- [ ] Implement regex-based parsing
- [ ] Add unit normalization
- [ ] Test biomarker extraction

### Phase 4: Integration
- [ ] Extend BiomarkerInputParser
- [ ] Update mediguard_bot.py webhook
- [ ] Add user feedback messages
- [ ] Add error handling
- [ ] Test end-to-end

### Phase 5: Testing & Polish
- [ ] Write unit tests
- [ ] Test with various formats
- [ ] Optimize accuracy
- [ ] Add logging
- [ ] Update documentation

---

## 🎯 Success Criteria

✅ Users can upload PDF/image lab reports via WhatsApp
✅ Bot automatically extracts biomarker values
✅ Extraction accuracy >85%
✅ Processing time <10 seconds
✅ Graceful error handling with helpful messages
✅ Works with existing prediction pipeline
✅ No breaking changes to existing functionality

---

## 📚 References

- **Expense Analyzer:** `expense_analyzer/` - Reference implementation
- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **Gemini Vision API:** https://ai.google.dev/docs
- **Twilio Media API:** https://www.twilio.com/docs/whatsapp/api/media

---

**Ready to implement!** 🚀

This plan provides a complete roadmap for implementing PDF OCR functionality in the MediGuard bot, following the same hybrid approach (LLM + Tesseract) used in the expense_analyzer.

