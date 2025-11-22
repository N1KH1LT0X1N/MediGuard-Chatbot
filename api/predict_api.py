"""
MediGuard Prediction API
REST API endpoint for disease prediction.
"""

import json
from flask import Flask, request, jsonify
from typing import Dict, Any

from mediguard.models.scaler import BiomarkerScaler
from mediguard.models.predictor import MediGuardPredictor
from mediguard.parsers.input_parser import BiomarkerInputParser
from mediguard.knowledge.rag_engine import MedicalRAGEngine


app = Flask(__name__)

# Initialize components
scaler = BiomarkerScaler()
predictor = MediGuardPredictor()
parser = BiomarkerInputParser()
rag_engine = MedicalRAGEngine()


@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Prediction endpoint.

    Request JSON:
    {
        "biomarkers": {
            "hemoglobin": 14.5,
            "wbc_count": 7.2,
            ...
        }
    }

    Response JSON:
    {
        "prediction": {
            "category": "sepsis",
            "confidence": 0.85,
            "severity": "critical",
            "probabilities": {...},
            "key_biomarkers": [...],
            "explanation": "..."
        },
        "warnings": [...],
        "references": [...]
    }
    """
    try:
        data = request.get_json()

        if not data or "biomarkers" not in data:
            return jsonify({
                "error": "Missing 'biomarkers' field in request"
            }), 400

        biomarker_values = data["biomarkers"]

        # Validate input is a dictionary
        if not isinstance(biomarker_values, dict):
            return jsonify({
                "error": "biomarkers must be a dictionary/object"
            }), 400

        # Scale biomarkers
        scaling_result = scaler.scale_all(biomarker_values)
        scaled_values = scaling_result["scaled_values"]
        warnings = scaling_result["warnings"]

        # Make prediction
        prediction_result = predictor.predict(scaled_values, biomarker_values)

        # Retrieve references
        references = rag_engine.retrieve_references(
            prediction_result["prediction"],
            max_results=3
        )

        # Return response
        return jsonify({
            "status": "success",
            "prediction": prediction_result,
            "warnings": warnings,
            "references": references,
            "raw_summary": scaling_result["raw_summary"],
        }), 200

    except ValueError as e:
        return jsonify({
            "error": f"Validation error: {str(e)}"
        }), 400

    except Exception as e:
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500


@app.route("/api/biomarkers", methods=["GET"])
def get_biomarkers():
    """
    Get list of all biomarkers with metadata.

    Response JSON:
    {
        "biomarkers": [
            {
                "id": "hemoglobin",
                "name": "Hemoglobin",
                "code": "HGB",
                "unit": "g/dL",
                "normal_range": {"min": 12.0, "max": 17.5},
                ...
            },
            ...
        ]
    }
    """
    biomarkers = scaler.get_all_biomarkers()
    return jsonify({"biomarkers": biomarkers}), 200


@app.route("/api/template", methods=["GET"])
def get_template():
    """
    Get input template.

    Query params:
        format: "json" | "key_value" | "csv"

    Response:
        Plain text template
    """
    format_type = request.args.get("format", "json")
    template = parser.get_template(format_type)

    return template, 200, {"Content-Type": "text/plain"}


@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "service": "mediguard-api",
        "version": "1.0.0"
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
