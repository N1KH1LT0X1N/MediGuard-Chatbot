"""
Test OCR Pipeline with health_report.pdf and health_report.jpg
Tests the complete flow: OCR → Biomarker Extraction → Prediction
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from mediguard.parsers.lab_report_ocr import LabReportOCR
from mediguard.parsers.biomarker_extractor import BiomarkerExtractor
from mediguard.utils.media_handler import MediaHandler

def test_file_processing(file_path: str, file_type: str):
    """Test processing a single file."""
    print(f"\n{'='*60}")
    print(f"Testing {file_type}: {file_path}")
    print(f"{'='*60}\n")
    
    if not os.path.exists(file_path):
        print(f"[ERROR] File not found: {file_path}")
        return False
    
    # Initialize components
    ocr_engine = LabReportOCR(use_llm=True)
    biomarker_extractor = BiomarkerExtractor(use_llm=True)
    media_handler = MediaHandler()
    
    try:
        # Step 1: Validate file
        print(f"[1/4] Validating file...")
        is_valid, error = media_handler.is_valid_lab_report(file_path)
        if not is_valid:
            print(f"[ERROR] File validation failed: {error}")
            return False
        print(f"[OK] File is valid")
        
        # Step 2: OCR Extraction
        print(f"\n[2/4] Extracting text with OCR...")
        ocr_result = ocr_engine.extract_text(file_path)
        ocr_text = ocr_result.get("text", "")
        ocr_method = ocr_result.get("method", "unknown")
        
        if not ocr_text or len(ocr_text.strip()) < 50:
            print(f"[ERROR] OCR extraction failed or returned too little text")
            print(f"   Method: {ocr_method}")
            print(f"   Text length: {len(ocr_text)}")
            return False
        
        print(f"[OK] OCR extraction successful")
        print(f"   Method: {ocr_method}")
        print(f"   Text length: {len(ocr_text)} characters")
        print(f"   First 200 chars: {ocr_text[:200]}...")
        
        # Step 3: Biomarker Extraction
        print(f"\n[3/4] Extracting biomarker values...")
        biomarker_values, extraction_errors = biomarker_extractor.extract_from_text(ocr_text)
        
        if not biomarker_values:
            print(f"[ERROR] Biomarker extraction failed")
            print(f"   Errors: {extraction_errors}")
            return False
        
        # Count found biomarkers
        found_biomarkers = sum(1 for v in biomarker_values.values() if v is not None)
        print(f"[OK] Biomarker extraction successful")
        print(f"   Found: {found_biomarkers}/24 biomarkers")
        
        # Show extracted values
        print(f"\n   Extracted values:")
        for bio_id, value in sorted(biomarker_values.items()):
            if value is not None:
                print(f"     {bio_id}: {value}")
        
        if extraction_errors:
            print(f"\n   Extraction warnings: {extraction_errors[:3]}")
        
        # Step 4: Validation
        print(f"\n[4/4] Validating extraction...")
        if found_biomarkers < 5:
            print(f"[WARN] Too few biomarkers found ({found_biomarkers}/24)")
            return False
        
        print(f"[OK] Extraction validation passed")
        print(f"\n{'='*60}")
        print(f"[SUCCESS] {file_type} processed successfully!")
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error processing {file_type}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_google_drive_url():
    """Test Google Drive URL download and processing."""
    print(f"\n{'='*60}")
    print(f"Testing Google Drive URL")
    print(f"{'='*60}\n")
    
    drive_url = "https://drive.google.com/file/d/1NUdDVck6Tv60JvLpojAVv22C8RD02kvf/view?usp=drivesdk"
    
    # Initialize components
    media_handler = MediaHandler()
    ocr_engine = LabReportOCR(use_llm=True)
    biomarker_extractor = BiomarkerExtractor(use_llm=True)
    
    try:
        # Step 1: Convert Google Drive URL to direct download
        print(f"[1/5] Converting Google Drive URL...")
        import re
        gd_pattern = r'/file/d/([a-zA-Z0-9_-]+)'
        match = re.search(gd_pattern, drive_url)
        if match:
            file_id = match.group(1)
            direct_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            print(f"[OK] Converted to direct download URL")
            print(f"   Original: {drive_url[:80]}...")
            print(f"   Direct: {direct_url[:80]}...")
        else:
            print(f"[ERROR] Could not extract file ID from URL")
            return False
        
        # Step 2: Download from URL
        print(f"\n[2/5] Downloading from Google Drive...")
        file_path, error = media_handler.download_media(
            direct_url,
            account_sid=None,  # Public URL, no auth needed
            auth_token=None,
            file_extension=".pdf"
        )
        
        if error or not file_path:
            print(f"[ERROR] Download failed: {error}")
            return False
        
        print(f"[OK] Downloaded successfully")
        print(f"   File: {file_path}")
        
        # Step 3: Validate file
        print(f"\n[3/5] Validating downloaded file...")
        is_valid, validation_error = media_handler.is_valid_lab_report(file_path)
        if not is_valid:
            print(f"[ERROR] File validation failed: {validation_error}")
            media_handler.cleanup_temp_file(file_path)
            return False
        print(f"[OK] File is valid")
        
        # Step 4: OCR Extraction
        print(f"\n[4/5] Extracting text with OCR...")
        ocr_result = ocr_engine.extract_text(file_path)
        ocr_text = ocr_result.get("text", "")
        ocr_method = ocr_result.get("method", "unknown")
        
        if not ocr_text or len(ocr_text.strip()) < 50:
            print(f"[ERROR] OCR extraction failed")
            media_handler.cleanup_temp_file(file_path)
            return False
        
        print(f"[OK] OCR extraction successful ({ocr_method}): {len(ocr_text)} characters")
        
        # Step 5: Biomarker Extraction
        print(f"\n[5/5] Extracting biomarker values...")
        biomarker_values, extraction_errors = biomarker_extractor.extract_from_text(ocr_text)
        
        if not biomarker_values:
            print(f"[ERROR] Biomarker extraction failed")
            print(f"   Errors: {extraction_errors}")
            media_handler.cleanup_temp_file(file_path)
            return False
        
        found_biomarkers = sum(1 for v in biomarker_values.values() if v is not None)
        print(f"[OK] Biomarker extraction successful: {found_biomarkers}/24 biomarkers")
        
        # Cleanup
        media_handler.cleanup_temp_file(file_path)
        
        print(f"\n{'='*60}")
        print(f"[SUCCESS] Google Drive URL processed successfully!")
        print(f"{'='*60}\n")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error processing Google Drive URL: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing OCR Pipeline with health_report files")
    print("=" * 60)
    
    # Test files
    test_files = [
        ("health_report.pdf", "PDF"),
        ("health_report.jpg", "Image"),
    ]
    
    results = {}
    
    # Test local files
    for file_path, file_type in test_files:
        if os.path.exists(file_path):
            results[file_type] = test_file_processing(file_path, file_type)
        else:
            print(f"⚠️  File not found: {file_path}")
            results[file_type] = False
    
    # Test Google Drive URL
    results["Google Drive"] = test_google_drive_url()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for test_name, success in results.items():
        status = "[PASS]" if success else "[FAIL]"
        print(f"  {test_name}: {status}")
    print("=" * 60)

