"""
Biomarker Extractor Module
Extracts biomarker values from OCR-extracted text using LLM and regex.
"""

import os
import re
import json
from typing import Dict, Optional, List, Tuple, Any

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

from mediguard.parsers.input_parser import BiomarkerInputParser


class BiomarkerExtractor:
    """
    Extracts biomarker values from OCR text.
    Uses LLM parsing (primary) with regex fallback.
    """

    # Standard biomarker order (24 biomarkers)
    BIOMARKER_ORDER = [
        "hemoglobin", "wbc_count", "platelet_count", "glucose", "creatinine",
        "bun", "sodium", "potassium", "chloride", "calcium",
        "alt", "ast", "bilirubin_total", "albumin", "total_protein",
        "ldh", "troponin", "bnp", "crp", "esr",
        "procalcitonin", "d_dimer", "inr", "lactate"
    ]

    # Biomarker name variations and aliases
    BIOMARKER_ALIASES = {
        # Hemoglobin
        "hgb": "hemoglobin", "hb": "hemoglobin", "hemo": "hemoglobin", "hgb": "hemoglobin",
        # WBC
        "wbc": "wbc_count", "white blood cell": "wbc_count", "white blood cell count": "wbc_count",
        "leukocyte": "wbc_count", "leukocyte count": "wbc_count",
        # Platelet
        "plt": "platelet_count", "platelet": "platelet_count", "platelets": "platelet_count",
        "thrombocyte": "platelet_count",
        # Glucose
        "glu": "glucose", "blood sugar": "glucose", "bg": "glucose", "blood glucose": "glucose",
        # Creatinine
        "creat": "creatinine", "cr": "creatinine", "creatinine": "creatinine",
        # BUN
        "bun": "bun", "blood urea nitrogen": "bun", "urea": "bun",
        # Sodium
        "na": "sodium", "sodium": "sodium",
        # Potassium
        "k": "potassium", "potassium": "potassium",
        # Chloride
        "cl": "chloride", "chloride": "chloride",
        # Calcium
        "ca": "calcium", "calcium": "calcium",
        # ALT
        "alt": "alt", "alanine aminotransferase": "alt", "sgot": "alt",
        # AST
        "ast": "ast", "aspartate aminotransferase": "ast", "sgpt": "ast",
        # Bilirubin
        "tbil": "bilirubin_total", "bilirubin": "bilirubin_total", "total bilirubin": "bilirubin_total",
        "tb": "bilirubin_total",
        # Albumin
        "alb": "albumin", "albumin": "albumin",
        # Total Protein
        "tp": "total_protein", "protein": "total_protein", "total protein": "total_protein",
        # LDH
        "ldh": "ldh", "lactate dehydrogenase": "ldh",
        # Troponin
        "tni": "troponin", "troponin": "troponin", "troponin i": "troponin", "ctni": "troponin",
        # BNP
        "bnp": "bnp", "b-type natriuretic peptide": "bnp", "brain natriuretic peptide": "bnp",
        # CRP
        "crp": "crp", "c-reactive protein": "crp",
        # ESR
        "esr": "esr", "erythrocyte sedimentation rate": "esr", "sed rate": "esr",
        # Procalcitonin
        "pct": "procalcitonin", "procalcitonin": "procalcitonin",
        # D-Dimer
        "dd": "d_dimer", "ddimer": "d_dimer", "d-dimer": "d_dimer",
        # INR
        "inr": "inr", "international normalized ratio": "inr",
        # Lactate
        "lac": "lactate", "lactate": "lactate", "lactic acid": "lactate",
    }

    def __init__(self, use_llm: bool = True):
        """
        Initialize biomarker extractor.

        Args:
            use_llm: Whether to use LLM for parsing (default: True)
        """
        self.use_llm = use_llm and GEMINI_AVAILABLE
        self.parser = BiomarkerInputParser()

    def extract_from_text(self, ocr_text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """
        Extract biomarker values from OCR text.

        Args:
            ocr_text: Text extracted from lab report

        Returns:
            Tuple of (parsed_values_dict, error_messages)
            Returns (None, errors) if extraction fails
        """
        if not ocr_text or len(ocr_text.strip()) < 10:
            return None, ["OCR text is too short or empty"]

        # Try LLM parsing first
        if self.use_llm:
            try:
                result = self.extract_with_llm(ocr_text)
                if result:
                    # Validate extracted values
                    validated, errors = self._validate_extracted_values(result)
                    if validated:
                        return validated, []
                    else:
                        print(f"[WARN] LLM extraction validation failed, trying regex fallback")
            except Exception as e:
                print(f"[WARN] LLM extraction failed: {str(e)}, trying regex fallback")

        # Fallback to regex parsing
        try:
            result = self.extract_with_regex(ocr_text)
            if result:
                validated, errors = self._validate_extracted_values(result)
                return validated, errors
        except Exception as e:
            return None, [f"Regex extraction failed: {str(e)}"]

        return None, ["Could not extract biomarker values from OCR text"]

    def extract_with_llm(self, ocr_text: str) -> Optional[Dict[str, float]]:
        """
        Extract biomarkers using Gemini LLM.

        Args:
            ocr_text: OCR-extracted text

        Returns:
            Dictionary of biomarker values or None
        """
        if not GEMINI_AVAILABLE:
            raise RuntimeError("Gemini API not configured")

        try:
            model = genai.GenerativeModel(GEMINI_MODEL)

            # Create comprehensive prompt
            prompt = f"""Extract all biomarker values from this lab report text. Return ONLY valid JSON with all 24 biomarkers.

Required biomarkers:
1. hemoglobin (HGB, Hb)
2. wbc_count (WBC, White Blood Cell)
3. platelet_count (PLT, Platelet)
4. glucose (GLU, Blood Sugar)
5. creatinine (CREAT, Cr)
6. bun (BUN, Blood Urea Nitrogen)
7. sodium (Na)
8. potassium (K)
9. chloride (Cl)
10. calcium (Ca)
11. alt (ALT, Alanine Aminotransferase)
12. ast (AST, Aspartate Aminotransferase)
13. bilirubin_total (TBIL, Total Bilirubin)
14. albumin (ALB)
15. total_protein (TP, Protein)
16. ldh (LDH, Lactate Dehydrogenase)
17. troponin (TnI, Troponin I)
18. bnp (BNP, B-Type Natriuretic Peptide)
19. crp (CRP, C-Reactive Protein)
20. esr (ESR, Erythrocyte Sedimentation Rate)
21. procalcitonin (PCT)
22. d_dimer (DD, D-Dimer)
23. inr (INR, International Normalized Ratio)
24. lactate (LAC, Lactate)

Lab Report Text:
{ocr_text[:4000]}  # Limit to avoid token limits

Return JSON format:
{{
  "hemoglobin": <number or null>,
  "wbc_count": <number or null>,
  "platelet_count": <number or null>,
  ...
}}

Rules:
- Extract numeric values only (no units in JSON)
- Use null for missing biomarkers
- Convert units to standard (e.g., g/dL for hemoglobin, mg/dL for glucose)
- Return ONLY the JSON object, no explanations
"""

            response = model.generate_content(prompt)
            response_text = response.text.strip()

            # Extract JSON from response (may have markdown code blocks)
            json_match = re.search(r'\{[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Try to parse entire response as JSON
                json_str = response_text

            # Parse JSON
            data = json.loads(json_str)

            # Convert to float values, handle null
            result = {}
            for biomarker_id in self.BIOMARKER_ORDER:
                value = data.get(biomarker_id)
                if value is not None:
                    try:
                        result[biomarker_id] = float(value)
                    except (ValueError, TypeError):
                        result[biomarker_id] = None
                else:
                    result[biomarker_id] = None

            return result

        except json.JSONDecodeError as e:
            print(f"[WARN] Failed to parse LLM JSON response: {str(e)}")
            return None
        except Exception as e:
            print(f"[WARN] LLM extraction error: {str(e)}")
            return None

    def extract_with_regex(self, ocr_text: str) -> Optional[Dict[str, float]]:
        """
        Extract biomarkers using regex patterns (fallback method).

        Args:
            ocr_text: OCR-extracted text

        Returns:
            Dictionary of biomarker values or None
        """
        result = {}
        text_lower = ocr_text.lower()

        # Pattern: biomarker name followed by number and optional unit
        # Example: "Hemoglobin: 14.5 g/dL" or "HGB 14.5"
        patterns = {}

        for biomarker_id in self.BIOMARKER_ORDER:
            aliases = [k for k, v in self.BIOMARKER_ALIASES.items() if v == biomarker_id]
            aliases.append(biomarker_id)

            # Create pattern for this biomarker
            name_pattern = "|".join(re.escape(alias) for alias in aliases)
            # Match: name, optional colon/equals, whitespace, number, optional unit
            pattern = rf'\b(?:{name_pattern})\b\s*[:=]?\s*(\d+\.?\d*)\s*(?:g/dl|mg/dl|mmol/l|×10³/μl|/μl|pg/ml|ng/ml|ratio|mm/hr|μg/ml)?'

            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            values = []
            for match in matches:
                try:
                    value = float(match.group(1))
                    values.append(value)
                except ValueError:
                    continue

            # Take the first reasonable value found
            if values:
                result[biomarker_id] = values[0]
            else:
                result[biomarker_id] = None

        # Check if we found at least some values
        found_count = sum(1 for v in result.values() if v is not None)
        if found_count < 5:  # Need at least 5 biomarkers
            return None

        return result

    def _validate_extracted_values(self, values: Dict[str, Optional[float]]) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """
        Validate and normalize extracted biomarker values.

        Args:
            values: Dictionary of extracted values (may contain None)

        Returns:
            Tuple of (validated_dict, error_messages)
        """
        validated = {}
        errors = []
        missing = []

        for biomarker_id in self.BIOMARKER_ORDER:
            value = values.get(biomarker_id)
            if value is None:
                missing.append(biomarker_id)
            else:
                try:
                    float_value = float(value)
                    # Basic range validation (very permissive)
                    if float_value < 0 or float_value > 100000:
                        errors.append(f"{biomarker_id}: value {float_value} out of reasonable range")
                    else:
                        validated[biomarker_id] = float_value
                except (ValueError, TypeError):
                    errors.append(f"{biomarker_id}: invalid value {value}")

        # If too many missing, return None
        if len(missing) > 19:  # Need at least 5 biomarkers
            return None, [f"Too many missing biomarkers: {len(missing)}/24"]

        # Fill missing with None (will be handled by parser)
        for biomarker_id in self.BIOMARKER_ORDER:
            if biomarker_id not in validated:
                validated[biomarker_id] = None

        return validated, errors

    def normalize_biomarker_name(self, text: str) -> Optional[str]:
        """
        Normalize biomarker name to standard ID.

        Args:
            text: Biomarker name from text

        Returns:
            Standard biomarker ID or None
        """
        text_lower = text.lower().strip()
        return self.BIOMARKER_ALIASES.get(text_lower)

