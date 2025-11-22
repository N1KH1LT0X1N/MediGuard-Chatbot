"""
Input Parser Module
Parses biomarker values from WhatsApp messages.
"""

import re
from typing import Dict, Optional, Tuple, List


class BiomarkerInputParser:
    """
    Parses biomarker input from various formats:
    - JSON format: {"hemoglobin": 14.5, "wbc_count": 7.2, ...}
    - Key-value format: hemoglobin=14.5, wbc_count=7.2, ...
    - CSV format: 14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5
    """

    # Standard biomarker order (24 biomarkers)
    BIOMARKER_ORDER = [
        "hemoglobin", "wbc_count", "platelet_count", "glucose", "creatinine",
        "bun", "sodium", "potassium", "chloride", "calcium",
        "alt", "ast", "bilirubin_total", "albumin", "total_protein",
        "ldh", "troponin", "bnp", "crp", "esr",
        "procalcitonin", "d_dimer", "inr", "lactate"
    ]

    # Aliases for biomarker codes
    BIOMARKER_ALIASES = {
        "hgb": "hemoglobin", "hb": "hemoglobin", "hemo": "hemoglobin",
        "wbc": "wbc_count", "white_blood_cell": "wbc_count",
        "plt": "platelet_count", "platelet": "platelet_count",
        "glu": "glucose", "blood_sugar": "glucose", "bg": "glucose",
        "creat": "creatinine", "cr": "creatinine",
        "na": "sodium",
        "k": "potassium",
        "cl": "chloride",
        "ca": "calcium",
        "tbil": "bilirubin_total", "bilirubin": "bilirubin_total",
        "alb": "albumin",
        "tp": "total_protein", "protein": "total_protein",
        "tni": "troponin", "troponin_i": "troponin",
        "dd": "d_dimer", "ddimer": "d_dimer",
        "lac": "lactate",
        "pct": "procalcitonin"
    }

    def parse(self, text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """
        Parse biomarker values from text input.

        Args:
            text: Input text from user

        Returns:
            Tuple of (parsed_values_dict, error_messages)
            Returns (None, errors) if parsing fails
        """
        text = text.strip()

        # Try JSON format first
        if text.startswith("{"):
            return self._parse_json(text)

        # Try key-value format
        if "=" in text or ":" in text:
            return self._parse_key_value(text)

        # Try CSV format (comma-separated values)
        if "," in text:
            return self._parse_csv(text)

        return None, ["Could not parse input format. Please use JSON, key=value, or CSV format."]

    def _parse_json(self, text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """Parse JSON format input."""
        import json
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                return None, ["JSON input must be a dictionary/object"]

            # Normalize keys
            normalized = {}
            for key, value in data.items():
                norm_key = self._normalize_biomarker_name(key)
                if norm_key is None:
                    return None, [f"Unknown biomarker: {key}"]

                try:
                    normalized[norm_key] = float(value)
                except (ValueError, TypeError):
                    return None, [f"Invalid numeric value for {key}: {value}"]

            # Validate all required biomarkers are present
            missing = self._check_missing_biomarkers(normalized)
            if missing:
                return None, [f"Missing required biomarkers: {', '.join(missing)}"]

            return normalized, []

        except json.JSONDecodeError as e:
            return None, [f"Invalid JSON format: {str(e)}"]

    def _parse_key_value(self, text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """Parse key=value or key:value format."""
        # Split by comma or newline
        pairs = re.split(r'[,\n]', text)

        result = {}
        for pair in pairs:
            pair = pair.strip()
            if not pair:
                continue

            # Try = separator
            if "=" in pair:
                parts = pair.split("=", 1)
            elif ":" in pair:
                parts = pair.split(":", 1)
            else:
                continue

            if len(parts) != 2:
                continue

            key, value = parts[0].strip(), parts[1].strip()

            # Normalize biomarker name
            norm_key = self._normalize_biomarker_name(key)
            if norm_key is None:
                return None, [f"Unknown biomarker: {key}"]

            # Parse value
            try:
                result[norm_key] = float(value)
            except (ValueError, TypeError):
                return None, [f"Invalid numeric value for {key}: {value}"]

        # Check for missing biomarkers
        missing = self._check_missing_biomarkers(result)
        if missing:
            return None, [f"Missing required biomarkers: {', '.join(missing)}"]

        return result, []

    def _parse_csv(self, text: str) -> Tuple[Optional[Dict[str, float]], List[str]]:
        """Parse CSV format (values in standard order)."""
        values = [v.strip() for v in text.split(",")]

        if len(values) != len(self.BIOMARKER_ORDER):
            return None, [
                f"CSV format requires exactly {len(self.BIOMARKER_ORDER)} values. "
                f"Got {len(values)}. Order: {', '.join(self.BIOMARKER_ORDER)}"
            ]

        result = {}
        for i, biomarker_id in enumerate(self.BIOMARKER_ORDER):
            try:
                result[biomarker_id] = float(values[i])
            except (ValueError, TypeError):
                return None, [
                    f"Invalid numeric value at position {i+1} ({biomarker_id}): {values[i]}"
                ]

        return result, []

    def _normalize_biomarker_name(self, name: str) -> Optional[str]:
        """Normalize biomarker name to standard ID."""
        name_lower = name.lower().strip().replace(" ", "_").replace("-", "_")

        # Check if it's already a standard ID
        if name_lower in self.BIOMARKER_ORDER:
            return name_lower

        # Check aliases
        if name_lower in self.BIOMARKER_ALIASES:
            return self.BIOMARKER_ALIASES[name_lower]

        return None

    def _check_missing_biomarkers(self, parsed: Dict[str, float]) -> List[str]:
        """Check for missing required biomarkers."""
        missing = []
        for bio_id in self.BIOMARKER_ORDER:
            if bio_id not in parsed:
                missing.append(bio_id)
        return missing

    def get_template(self, format_type: str = "json") -> str:
        """
        Get an input template in the specified format.

        Args:
            format_type: "json", "key_value", or "csv"

        Returns:
            Template string
        """
        if format_type == "json":
            template = "{\n"
            for bio_id in self.BIOMARKER_ORDER:
                template += f'  "{bio_id}": 0.0,\n'
            template = template.rstrip(",\n") + "\n}"
            return template

        elif format_type == "key_value":
            pairs = [f"{bio_id}=0.0" for bio_id in self.BIOMARKER_ORDER]
            return ", ".join(pairs)

        elif format_type == "csv":
            return ", ".join(["0.0"] * len(self.BIOMARKER_ORDER))

        else:
            return "Unknown format type"
