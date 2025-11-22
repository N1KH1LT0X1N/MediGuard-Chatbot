"""
MediGuard Predictor Module
Machine learning model for disease prediction based on biomarkers.
"""

import json
import os
import numpy as np
from typing import Dict, List, Any, Optional, Tuple


class MediGuardPredictor:
    """
    Predicts disease categories from biomarker values.
    Uses a rule-based + ML hybrid approach for clinical triage.
    """

    def __init__(self, biomarker_config_path: Optional[str] = None):
        """
        Initialize predictor with disease categories and rules.

        Args:
            biomarker_config_path: Path to biomarkers.json config
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

        self.disease_categories = {d["id"]: d for d in config["disease_categories"]}
        self.biomarkers = {b["id"]: b for b in config["biomarkers"]}

    def predict(
        self,
        scaled_values: List[float],
        raw_values: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Predict disease category from biomarker values.

        Args:
            scaled_values: List of 24 scaled biomarker values [0-1]
            raw_values: Dict of raw biomarker values

        Returns:
            Dict containing:
                - prediction: Disease category ID
                - confidence: Confidence score [0-1]
                - probabilities: Dict of all category probabilities
                - key_biomarkers: List of top contributing biomarkers
                - explanation: Text explanation of the prediction
        """
        # Use rule-based system for clinical triage
        # In production, this would be replaced with a trained ML model

        probabilities = self._compute_probabilities(raw_values)
        prediction = max(probabilities, key=probabilities.get)
        confidence = probabilities[prediction]

        # Identify key biomarkers driving the prediction
        key_biomarkers = self._identify_key_biomarkers(raw_values, prediction)

        # Generate explanation
        explanation = self._generate_explanation(prediction, key_biomarkers, raw_values)

        return {
            "prediction": prediction,
            "prediction_name": self.disease_categories[prediction]["name"],
            "confidence": round(confidence, 3),
            "severity": self.disease_categories[prediction]["severity"],
            "probabilities": {
                cat_id: round(prob, 3)
                for cat_id, prob in sorted(
                    probabilities.items(),
                    key=lambda x: x[1],
                    reverse=True
                )
            },
            "key_biomarkers": key_biomarkers,
            "explanation": explanation,
        }

    def _compute_probabilities(self, raw_values: Dict[str, float]) -> Dict[str, float]:
        """
        Compute probability scores for each disease category.
        Uses rule-based clinical criteria.
        """
        scores = {cat_id: 0.0 for cat_id in self.disease_categories.keys()}

        # Sepsis indicators
        if raw_values.get("procalcitonin", 0) > 2.0:
            scores["sepsis"] += 0.4
        if raw_values.get("lactate", 0) > 4.0:
            scores["sepsis"] += 0.3
        if raw_values.get("wbc_count", 0) > 12.0 or raw_values.get("wbc_count", 0) < 4.0:
            scores["sepsis"] += 0.2
        if raw_values.get("crp", 0) > 100:
            scores["sepsis"] += 0.1

        # Cardiac event indicators
        if raw_values.get("troponin", 0) > 0.04:
            scores["cardiac_event"] += 0.5
        if raw_values.get("bnp", 0) > 400:
            scores["cardiac_event"] += 0.3
        if raw_values.get("ldh", 0) > 500:
            scores["cardiac_event"] += 0.2

        # Renal failure indicators
        if raw_values.get("creatinine", 0) > 2.0:
            scores["renal_failure"] += 0.4
        if raw_values.get("bun", 0) > 40:
            scores["renal_failure"] += 0.3
        if raw_values.get("potassium", 0) > 5.5:
            scores["renal_failure"] += 0.2
        if raw_values.get("creatinine", 0) / max(raw_values.get("bun", 1), 1) < 0.05:
            scores["renal_failure"] += 0.1

        # Liver disease indicators
        if raw_values.get("alt", 0) > 200 or raw_values.get("ast", 0) > 200:
            scores["liver_disease"] += 0.4
        if raw_values.get("bilirubin_total", 0) > 2.0:
            scores["liver_disease"] += 0.3
        if raw_values.get("albumin", 0) < 3.0:
            scores["liver_disease"] += 0.2
        if raw_values.get("inr", 0) > 1.5:
            scores["liver_disease"] += 0.1

        # Metabolic disorder indicators
        if raw_values.get("glucose", 0) > 200 or raw_values.get("glucose", 0) < 60:
            scores["metabolic_disorder"] += 0.4
        if abs(raw_values.get("sodium", 140) - 140) > 10:
            scores["metabolic_disorder"] += 0.3
        if raw_values.get("calcium", 9.5) < 7.0 or raw_values.get("calcium", 9.5) > 11.0:
            scores["metabolic_disorder"] += 0.3

        # Coagulopathy indicators
        if raw_values.get("inr", 0) > 2.0:
            scores["coagulopathy"] += 0.4
        if raw_values.get("d_dimer", 0) > 2.0:
            scores["coagulopathy"] += 0.3
        if raw_values.get("platelet_count", 0) < 100:
            scores["coagulopathy"] += 0.3

        # Anemia indicators
        if raw_values.get("hemoglobin", 0) < 10.0:
            scores["anemia"] += 0.6
        if raw_values.get("hemoglobin", 0) < 7.0:
            scores["anemia"] += 0.4

        # Infection indicators
        if raw_values.get("wbc_count", 0) > 11.0:
            scores["infection"] += 0.3
        if raw_values.get("crp", 0) > 10:
            scores["infection"] += 0.3
        if raw_values.get("esr", 0) > 30:
            scores["infection"] += 0.2
        if raw_values.get("procalcitonin", 0) > 0.25:
            scores["infection"] += 0.2

        # Normalize scores to probabilities
        total = sum(scores.values())
        if total > 0:
            probabilities = {k: v / total for k, v in scores.items()}
        else:
            # All normal
            probabilities = {k: 0.0 for k in scores.keys()}
            probabilities["normal"] = 1.0

        return probabilities

    def _identify_key_biomarkers(
        self,
        raw_values: Dict[str, float],
        prediction: str
    ) -> List[Dict[str, Any]]:
        """
        Identify top biomarkers contributing to the prediction.

        Returns list of dicts with biomarker info and direction (↑/↓)
        """
        key_biomarkers = []

        # Disease-specific key biomarkers
        relevance_map = {
            "sepsis": ["procalcitonin", "lactate", "wbc_count", "crp"],
            "cardiac_event": ["troponin", "bnp", "ldh"],
            "renal_failure": ["creatinine", "bun", "potassium"],
            "liver_disease": ["alt", "ast", "bilirubin_total", "albumin", "inr"],
            "metabolic_disorder": ["glucose", "sodium", "calcium", "potassium"],
            "coagulopathy": ["inr", "d_dimer", "platelet_count"],
            "anemia": ["hemoglobin"],
            "infection": ["wbc_count", "crp", "esr", "procalcitonin"],
            "normal": [],
        }

        relevant_ids = relevance_map.get(prediction, [])

        for bio_id in relevant_ids:
            if bio_id not in raw_values:
                continue

            bio = self.biomarkers[bio_id]
            raw_val = raw_values[bio_id]

            # Determine direction
            if raw_val < bio["normal_range"]["min"]:
                direction = "↓"
                status = "LOW"
            elif raw_val > bio["normal_range"]["max"]:
                direction = "↑"
                status = "HIGH"
            else:
                direction = "→"
                status = "NORMAL"

            # Calculate deviation from normal
            normal_mid = (bio["normal_range"]["min"] + bio["normal_range"]["max"]) / 2
            deviation = abs(raw_val - normal_mid) / normal_mid

            key_biomarkers.append({
                "id": bio_id,
                "name": bio["name"],
                "code": bio["code"],
                "value": raw_val,
                "unit": bio["unit"],
                "direction": direction,
                "status": status,
                "deviation": round(deviation, 2),
            })

        # Sort by deviation (most abnormal first)
        key_biomarkers.sort(key=lambda x: x["deviation"], reverse=True)

        return key_biomarkers[:5]  # Top 5

    def _generate_explanation(
        self,
        prediction: str,
        key_biomarkers: List[Dict[str, Any]],
        raw_values: Dict[str, float]
    ) -> str:
        """Generate human-readable explanation of the prediction."""
        disease = self.disease_categories[prediction]

        if prediction == "normal":
            return "All biomarkers are within normal ranges. No significant abnormalities detected."

        explanation = f"Prediction indicates {disease['name']}. "

        if key_biomarkers:
            bio_desc = []
            for kb in key_biomarkers[:3]:  # Top 3
                bio_desc.append(
                    f"{kb['code']} is {kb['status']} "
                    f"({kb['direction']} {kb['value']} {kb['unit']})"
                )

            explanation += "Key findings: " + ", ".join(bio_desc) + ". "

        explanation += disease['description']

        return explanation
