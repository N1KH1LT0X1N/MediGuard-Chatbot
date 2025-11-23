"""
Lab Report OCR Module
Extracts text from PDF/image lab reports using hybrid approach (LLM + Tesseract).
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import pytesseract
    from PIL import Image
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    print("Warning: Tesseract OCR dependencies not installed. Install with: pip install pytesseract pillow pdf2image")

try:
    import google.generativeai as genai
    from dotenv import load_dotenv
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
    if GEMINI_AVAILABLE:
        genai.configure(api_key=GEMINI_API_KEY)
except Exception:
    GEMINI_AVAILABLE = False
    print("Warning: Gemini API not available. Tesseract will be used as fallback.")


class LabReportOCR:
    """
    Hybrid OCR engine for lab reports.
    Uses Gemini Vision API (primary) with Tesseract OCR fallback.
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize OCR engine.

        Args:
            use_llm: Whether to use LLM (Gemini) for extraction (default: True)
        """
        self.use_llm = use_llm and GEMINI_AVAILABLE
        self.tesseract_available = TESSERACT_AVAILABLE

        if not self.use_llm and not self.tesseract_available:
            raise RuntimeError(
                "No OCR method available. Install Tesseract or configure Gemini API key."
            )

        if self.use_llm:
            print("[OK] Lab Report OCR: Gemini Vision API enabled (primary)")
        if self.tesseract_available:
            print("[OK] Lab Report OCR: Tesseract enabled (fallback)")

    def extract_text(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from PDF/image lab report using hybrid approach.

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dictionary with:
                - text: Extracted text
                - method: "gemini" or "tesseract"
                - metadata: Additional info
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try LLM first (if enabled)
        if self.use_llm:
            try:
                print("[INFO] Attempting Gemini Vision extraction...")
                result = self.extract_with_llm(file_path)
                if result and result.get("text"):
                    print("[OK] Gemini extraction successful")
                    return result
                else:
                    print("[WARN] Gemini returned empty result, falling back to Tesseract")
            except Exception as e:
                print(f"[WARN] Gemini extraction failed: {str(e)}, falling back to Tesseract")

        # Fallback to Tesseract
        if self.tesseract_available:
            try:
                print("[INFO] Using Tesseract OCR extraction...")
                result = self.extract_with_tesseract(file_path)
                print("[OK] Tesseract extraction successful")
                return result
            except Exception as e:
                raise RuntimeError(f"Tesseract OCR failed: {str(e)}")

        raise RuntimeError("No OCR method available")

    def extract_with_llm(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text using Gemini Vision API.

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dictionary with extracted text and metadata
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini API not configured")

        try:
            # Load file
            path = Path(file_path)
            file_extension = path.suffix.lower()

            # For PDFs, convert to image first
            if file_extension == '.pdf':
                image = self.convert_pdf_to_image(file_path)
                # Save temporarily as image for Gemini
                import tempfile
                temp_image_path = tempfile.mktemp(suffix='.png')
                image.save(temp_image_path)
                file_to_process = temp_image_path
            else:
                file_to_process = file_path

            # Use Gemini Vision API
            model = genai.GenerativeModel(GEMINI_MODEL)

            # Determine MIME type
            if file_extension == '.pdf':
                mime_type = "image/png"  # PDF converted to PNG
            elif file_extension in ['.jpg', '.jpeg']:
                mime_type = "image/jpeg"
            elif file_extension == '.png':
                mime_type = "image/png"
            else:
                mime_type = "image/png"  # Default

            # Read image
            import base64
            with open(file_to_process, 'rb') as f:
                image_data = f.read()

            # Create prompt for text extraction
            prompt = """
            Extract all text from this lab report image. 
            Return the raw text content exactly as it appears, preserving:
            - All biomarker names and values
            - Units of measurement
            - Numbers and decimal values
            - Table structures if present
            
            Return only the extracted text, no explanations.
            """

            # Generate content with image
            # Gemini Vision API accepts image as part of content list
            # (genai is already imported at module level)
            
            # Create image part
            image_part = {
                "mime_type": mime_type,
                "data": image_data
            }
            
            # Generate content
            response = model.generate_content([prompt, image_part])

            # Cleanup temp file if created
            if file_extension == '.pdf' and 'temp_image_path' in locals():
                try:
                    os.unlink(temp_image_path)
                except:
                    pass

            extracted_text = response.text if hasattr(response, 'text') else ""

            return {
                "text": extracted_text,
                "method": "gemini",
                "metadata": {
                    "model": GEMINI_MODEL,
                    "file_type": file_extension,
                }
            }

        except Exception as e:
            raise RuntimeError(f"Gemini extraction failed: {str(e)}")

    def extract_with_tesseract(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text using Tesseract OCR.

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dictionary with extracted text and metadata
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("Tesseract OCR not available")

        try:
            # Load image (convert PDF if needed)
            image = self.load_image(file_path)
            path = Path(file_path)

            # Extract text with Tesseract
            print(f"[INFO] Running Tesseract OCR on {path.name}...")
            text = pytesseract.image_to_string(image, lang='eng')

            return {
                "text": text,
                "method": "tesseract",
                "metadata": {
                    "file_type": path.suffix.lower(),
                    "image_size": f"{image.size[0]}x{image.size[1]}",
                }
            }

        except Exception as e:
            raise RuntimeError(f"Tesseract OCR failed: {str(e)}")

    def load_image(self, file_path: str) -> Image.Image:
        """
        Load image from file path (supports PDF and image formats).

        Args:
            file_path: Path to file

        Returns:
            PIL Image object
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Handle PDF
        if path.suffix.lower() == '.pdf':
            print("[INFO] Converting PDF to image for OCR...")
            images = convert_from_path(file_path, first_page=1, last_page=1, dpi=300)
            if not images:
                raise ValueError("Failed to convert PDF to image")
            return images[0]

        # Handle images
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
            return Image.open(file_path)

        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")

    def convert_pdf_to_image(self, pdf_path: str) -> Image.Image:
        """
        Convert PDF to image for processing.

        Args:
            pdf_path: Path to PDF file

        Returns:
            PIL Image object
        """
        if not TESSERACT_AVAILABLE:
            raise RuntimeError("pdf2image not available")

        print("[INFO] Converting PDF to image...")
        images = convert_from_path(pdf_path, first_page=1, last_page=1, dpi=300)
        if not images:
            raise ValueError("Failed to convert PDF to image")
        return images[0]

