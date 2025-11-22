"""
Biomarker Scaler Module
Handles scaling and normalization of biomarker values.
"""

import json
import os
from typing import Dict, List, Tuple, Any, Optional


class BiomarkerScaler:
    """
    Scales biomarker values to normalized ranges for ML model input.
    Uses min-max scaling based on critical ranges.
    """

    def __init__(self, biomarker_config_path: Optional[str] = None):
        """
        Initialize scaler with biomarker configuration.

        Args:
            biomarker_config_path: Path to biomarkers.json config file
        """
        if biomarker_config_path is None:
            biomarker_config_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "data",
                "biomarkers.json"
            )

        with open(biomarker_config_path, "r") as f:
            config = json.load(f)

        self.biomarkers = {b["id"]: b for b in config["biomarkers"]}
        self.biomarker_order = [b["id"] for b in config["biomarkers"]]

    def scale_value(self, biomarker_id: str, raw_value: float) -> Tuple[float, List[str]]:
        """
        Scale a single biomarker value to [0, 1] range.

        Args:
            biomarker_id: ID of the biomarker
            raw_value: Raw measured value

        Returns:
            Tuple of (scaled_value, warnings_list)
        """
        if biomarker_id not in self.biomarkers:
            raise ValueError(f"Unknown biomarker: {biomarker_id}")

        bio = self.biomarkers[biomarker_id]
        warnings = []

        # Min-max scaling using critical ranges
        min_val = bio["critical_low"]
        max_val = bio["critical_high"]

        # Check for out-of-range values
        if raw_value < bio["normal_range"]["min"]:
            warnings.append(
                f"⚠️ {bio['name']} ({bio['code']}) is BELOW normal range "
                f"({raw_value} {bio['unit']} < {bio['normal_range']['min']} {bio['unit']})"
            )
        elif raw_value > bio["normal_range"]["max"]:
            warnings.append(
                f"⚠️ {bio['name']} ({bio['code']}) is ABOVE normal range "
                f"({raw_value} {bio['unit']} > {bio['normal_range']['max']} {bio['unit']})"
            )

        # Critical value warnings
        if raw_value < bio["critical_low"]:
            warnings.append(
                f"🚨 CRITICAL: {bio['name']} ({bio['code']}) is dangerously LOW: "
                f"{raw_value} {bio['unit']}"
            )
        elif raw_value > bio["critical_high"]:
            warnings.append(
                f"🚨 CRITICAL: {bio['name']} ({bio['code']}) is dangerously HIGH: "
                f"{raw_value} {bio['unit']}"
            )

        # Perform min-max scaling
        scaled = (raw_value - min_val) / (max_val - min_val)
        scaled = max(0.0, min(1.0, scaled))  # Clip to [0, 1]

        return scaled, warnings

    def scale_all(self, biomarker_values: Dict[str, float]) -> Dict[str, Any]:
        """
        Scale all biomarker values and collect warnings.

        Args:
            biomarker_values: Dict mapping biomarker_id to raw value

        Returns:
            Dict containing:
                - scaled_values: List of scaled values in standard order
                - warnings: List of warning messages
                - raw_summary: Dict of raw values with metadata
        """
        scaled_values = []
        all_warnings = []
        raw_summary = {}

        for bio_id in self.biomarker_order:
            if bio_id not in biomarker_values:
                raise ValueError(f"Missing biomarker value: {bio_id}")

            raw_val = biomarker_values[bio_id]
            scaled_val, warnings = self.scale_value(bio_id, raw_val)

            scaled_values.append(scaled_val)
            all_warnings.extend(warnings)

            bio = self.biomarkers[bio_id]
            raw_summary[bio_id] = {
                "name": bio["name"],
                "code": bio["code"],
                "raw_value": raw_val,
                "unit": bio["unit"],
                "scaled_value": round(scaled_val, 4),
                "normal_range": bio["normal_range"],
            }

        return {
            "scaled_values": scaled_values,
            "warnings": all_warnings,
            "raw_summary": raw_summary,
        }

    def get_biomarker_info(self, biomarker_id: str) -> Dict[str, Any]:
        """Get metadata for a specific biomarker."""
        if biomarker_id not in self.biomarkers:
            raise ValueError(f"Unknown biomarker: {biomarker_id}")
        return self.biomarkers[biomarker_id]

    def get_all_biomarkers(self) -> List[Dict[str, Any]]:
        """Get list of all biomarkers in standard order."""
        return [self.biomarkers[bio_id] for bio_id in self.biomarker_order]
