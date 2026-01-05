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

from mediguard.utils import llm_provider

LLM_AVAILABLE = llm_provider.GROQ_AVAILABLE
if not LLM_AVAILABLE:
    print("Warning: Groq API not available. Tesseract will be used as fallback.")


class LabReportOCR:
    """
    Hybrid OCR engine for lab reports.
    Uses Groq Vision API (primary) with Tesseract OCR fallback.
    """

    def __init__(self, use_llm: bool = True):
        """
        Initialize OCR engine.

        Args:
            use_llm: Whether to use LLM (Groq) for extraction (default: True)
        """
        self.use_llm = use_llm and LLM_AVAILABLE
        self.tesseract_available = TESSERACT_AVAILABLE

        if not self.use_llm and not self.tesseract_available:
            raise RuntimeError(
                "No OCR method available. Install Tesseract or configure Groq API key."
            )

        if self.use_llm:
            print("[OK] Lab Report OCR: Groq Vision API enabled (primary)")
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
                - method: "groq" or "tesseract"
                - metadata: Additional info
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Try LLM first (if enabled)
        if self.use_llm:
            try:
                print("[INFO] Attempting Groq Vision extraction...")
                result = self.extract_with_llm(file_path)
                if result and result.get("text"):
                    print("[OK] Groq extraction successful")
                    return result
                else:
                    print("[WARN] Groq returned empty result, falling back to Tesseract")
            except Exception as e:
                print(f"[WARN] Groq extraction failed: {str(e)}, falling back to Tesseract")

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
        Extract text using Groq Vision API.

        Args:
            file_path: Path to PDF or image file

        Returns:
            Dictionary with extracted text and metadata
        """
        if not LLM_AVAILABLE:
            raise RuntimeError("Groq API not configured")

        path = Path(file_path)
        file_extension = path.suffix.lower()
        temp_image_path = None

        try:
            # For PDFs, convert to image first
            if file_extension == '.pdf':
                image = self.convert_pdf_to_image(file_path)
                import tempfile
                temp_image_path = tempfile.mktemp(suffix='.png')
                image.save(temp_image_path)
                file_to_process = temp_image_path
            else:
                file_to_process = file_path

            # Create prompt for text extraction
            prompt = """Extract all text from this lab report image.

RULES:
- Return the raw text content exactly as it appears
- Preserve all biomarker names and values
- Preserve units of measurement
- Preserve numbers and decimal values
- Preserve table structures if present

Return only the extracted text, no explanations."""

            # Use Groq Vision via llm_provider
            extracted_text = llm_provider.generate_with_image(prompt, file_to_process)

            return {
                "text": extracted_text or "",
                "method": "groq",
                "metadata": {
                    "model": llm_provider.GROQ_VISION_MODEL,
                    "file_type": file_extension,
                }
            }

        except Exception as e:
            raise RuntimeError(f"Groq extraction failed: {str(e)}")

        finally:
            # Cleanup temp file
            if temp_image_path:
                try:
                    os.unlink(temp_image_path)
                except OSError:
                    pass


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

