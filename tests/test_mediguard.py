"""
Test Suite for MediGuard AI
"""

import pytest
import json
from mediguard.models.scaler import BiomarkerScaler
from mediguard.models.predictor import MediGuardPredictor
from mediguard.parsers.input_parser import BiomarkerInputParser
from mediguard.knowledge.rag_engine import MedicalRAGEngine
from mediguard.utils.security import anonymize_user_id, validate_input_security
from mediguard.utils.formatters import format_prediction_response, chunk_message


# ---------------------------
# Fixtures
# ---------------------------

@pytest.fixture
def normal_values():
    """Normal biomarker values for testing."""
    return {
        "hemoglobin": 14.5,
        "wbc_count": 7.2,
        "platelet_count": 250,
        "glucose": 95,
        "creatinine": 1.0,
        "bun": 15,
        "sodium": 138,
        "potassium": 4.2,
        "chloride": 102,
        "calcium": 9.5,
        "alt": 25,
        "ast": 30,
        "bilirubin_total": 0.8,
        "albumin": 4.0,
        "total_protein": 7.0,
        "ldh": 180,
        "troponin": 0.02,
        "bnp": 50,
        "crp": 1.5,
        "esr": 10,
        "procalcitonin": 0.03,
        "d_dimer": 0.3,
        "inr": 1.0,
        "lactate": 1.5,
    }


@pytest.fixture
def sepsis_values():
    """Biomarker values indicating sepsis."""
    return {
        "hemoglobin": 8.5,
        "wbc_count": 18.5,
        "platelet_count": 85,
        "glucose": 180,
        "creatinine": 2.1,
        "bun": 42,
        "sodium": 132,
        "potassium": 5.2,
        "chloride": 98,
        "calcium": 8.1,
        "alt": 85,
        "ast": 120,
        "bilirubin_total": 1.8,
        "albumin": 2.8,
        "total_protein": 5.5,
        "ldh": 420,
        "troponin": 0.08,
        "bnp": 280,
        "crp": 185,
        "esr": 65,
        "procalcitonin": 5.2,
        "d_dimer": 2.8,
        "inr": 1.6,
        "lactate": 6.5,
    }


# ---------------------------
# BiomarkerScaler Tests
# ---------------------------

def test_scaler_initialization():
    """Test scaler initializes correctly."""
    scaler = BiomarkerScaler()
    assert len(scaler.biomarkers) == 24
    assert "hemoglobin" in scaler.biomarkers


def test_scaler_normal_values(normal_values):
    """Test scaling of normal biomarker values."""
    scaler = BiomarkerScaler()
    result = scaler.scale_all(normal_values)

    assert "scaled_values" in result
    assert "warnings" in result
    assert "raw_summary" in result
    assert len(result["scaled_values"]) == 24

    # Normal values should have minimal warnings
    assert len(result["warnings"]) == 0


def test_scaler_abnormal_values(sepsis_values):
    """Test scaling detects abnormal values."""
    scaler = BiomarkerScaler()
    result = scaler.scale_all(sepsis_values)

    # Should generate warnings for abnormal values
    assert len(result["warnings"]) > 0

    # Check for specific critical warnings
    warning_text = " ".join(result["warnings"])
    assert "CRITICAL" in warning_text or "HIGH" in warning_text or "LOW" in warning_text


def test_scaler_missing_biomarker():
    """Test scaler raises error for missing biomarker."""
    scaler = BiomarkerScaler()
    incomplete_values = {"hemoglobin": 14.5}

    with pytest.raises(ValueError, match="Missing biomarker"):
        scaler.scale_all(incomplete_values)


# ---------------------------
# MediGuardPredictor Tests
# ---------------------------

def test_predictor_initialization():
    """Test predictor initializes correctly."""
    predictor = MediGuardPredictor()
    assert len(predictor.disease_categories) == 9


def test_predictor_normal_case(normal_values):
    """Test prediction for normal values."""
    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()

    scaling_result = scaler.scale_all(normal_values)
    prediction = predictor.predict(
        scaling_result["scaled_values"],
        normal_values
    )

    assert prediction["prediction"] == "normal"
    assert prediction["confidence"] > 0.9


def test_predictor_sepsis_case(sepsis_values):
    """Test prediction for sepsis case."""
    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()

    scaling_result = scaler.scale_all(sepsis_values)
    prediction = predictor.predict(
        scaling_result["scaled_values"],
        sepsis_values
    )

    assert prediction["prediction"] == "sepsis"
    assert prediction["confidence"] > 0.5
    assert prediction["severity"] == "critical"
    assert len(prediction["key_biomarkers"]) > 0


def test_predictor_cardiac_case():
    """Test prediction for cardiac event."""
    cardiac_values = {
        "hemoglobin": 13.2,
        "wbc_count": 8.5,
        "platelet_count": 220,
        "glucose": 110,
        "creatinine": 1.1,
        "bun": 18,
        "sodium": 139,
        "potassium": 4.0,
        "chloride": 101,
        "calcium": 9.2,
        "alt": 28,
        "ast": 42,
        "bilirubin_total": 0.9,
        "albumin": 3.8,
        "total_protein": 6.8,
        "ldh": 620,
        "troponin": 1.5,
        "bnp": 850,
        "crp": 8.5,
        "esr": 22,
        "procalcitonin": 0.04,
        "d_dimer": 0.8,
        "inr": 1.1,
        "lactate": 2.0,
    }

    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()

    scaling_result = scaler.scale_all(cardiac_values)
    prediction = predictor.predict(
        scaling_result["scaled_values"],
        cardiac_values
    )

    assert prediction["prediction"] == "cardiac_event"
    assert prediction["severity"] == "critical"


# ---------------------------
# BiomarkerInputParser Tests
# ---------------------------

def test_parser_json_format(normal_values):
    """Test parsing JSON format input."""
    parser = BiomarkerInputParser()
    json_input = json.dumps(normal_values)

    parsed, errors = parser.parse(json_input)

    assert parsed is not None
    assert len(errors) == 0
    assert parsed == normal_values


def test_parser_csv_format():
    """Test parsing CSV format input."""
    parser = BiomarkerInputParser()
    csv_input = "14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5"

    parsed, errors = parser.parse(csv_input)

    assert parsed is not None
    assert len(errors) == 0
    assert len(parsed) == 24


def test_parser_key_value_format():
    """Test parsing key-value format input."""
    parser = BiomarkerInputParser()
    kv_input = "hemoglobin=14.5, wbc_count=7.2, platelet_count=250, glucose=95, creatinine=1.0, bun=15, sodium=138, potassium=4.2, chloride=102, calcium=9.5, alt=25, ast=30, bilirubin_total=0.8, albumin=4.0, total_protein=7.0, ldh=180, troponin=0.02, bnp=50, crp=1.5, esr=10, procalcitonin=0.03, d_dimer=0.3, inr=1.0, lactate=1.5"

    parsed, errors = parser.parse(kv_input)

    assert parsed is not None
    assert len(errors) == 0


def test_parser_invalid_format():
    """Test parser handles invalid format."""
    parser = BiomarkerInputParser()
    invalid_input = "this is not valid biomarker data"

    parsed, errors = parser.parse(invalid_input)

    assert parsed is None
    assert len(errors) > 0


def test_parser_incomplete_data():
    """Test parser detects missing biomarkers."""
    parser = BiomarkerInputParser()
    incomplete = json.dumps({"hemoglobin": 14.5, "wbc_count": 7.2})

    parsed, errors = parser.parse(incomplete)

    assert parsed is None
    assert len(errors) > 0
    assert "Missing" in errors[0]


# ---------------------------
# MedicalRAGEngine Tests
# ---------------------------

def test_rag_initialization():
    """Test RAG engine initializes correctly."""
    rag = MedicalRAGEngine()
    assert len(rag.knowledge_base) > 0


def test_rag_retrieve_references():
    """Test retrieving references for disease category."""
    rag = MedicalRAGEngine()
    refs = rag.retrieve_references("sepsis", max_results=2)

    assert len(refs) > 0
    assert len(refs) <= 2
    assert "title" in refs[0]
    assert "citation" in refs[0]


def test_rag_query():
    """Test natural language query."""
    rag = MedicalRAGEngine()
    results = rag.query("troponin myocardial infarction")

    assert len(results) > 0
    assert any("troponin" in r["content"].lower() for r in results)


def test_rag_format_references():
    """Test reference formatting."""
    rag = MedicalRAGEngine()
    refs = rag.retrieve_references("cardiac_event")
    formatted = rag.format_references(refs)

    assert "References" in formatted
    assert "Citation" in formatted


# ---------------------------
# Security Tests
# ---------------------------

def test_anonymization():
    """Test user ID anonymization."""
    user_id = "whatsapp:+1234567890"
    anon1 = anonymize_user_id(user_id)
    anon2 = anonymize_user_id(user_id)

    # Same input should produce same hash
    assert anon1 == anon2

    # Hash should not contain original number
    assert "1234567890" not in anon1

    # Different inputs should produce different hashes
    anon3 = anonymize_user_id("whatsapp:+9876543210")
    assert anon1 != anon3


def test_input_validation_valid():
    """Test validation accepts valid input."""
    valid_input = json.dumps({"hemoglobin": 14.5})
    is_valid, error = validate_input_security(valid_input)

    assert is_valid is True
    assert error is None


def test_input_validation_sql_injection():
    """Test validation detects SQL injection."""
    malicious = "'; DROP TABLE sessions; --"
    is_valid, error = validate_input_security(malicious)

    assert is_valid is False
    assert "Suspicious pattern" in error


def test_input_validation_script_injection():
    """Test validation detects script injection."""
    malicious = "<script>alert('xss')</script>"
    is_valid, error = validate_input_security(malicious)

    assert is_valid is False
    assert "Suspicious pattern" in error


def test_input_validation_length():
    """Test validation rejects excessive length."""
    too_long = "a" * 20000
    is_valid, error = validate_input_security(too_long)

    assert is_valid is False
    assert "too long" in error


# ---------------------------
# Formatter Tests
# ---------------------------

def test_chunk_message_short():
    """Test chunking short message."""
    short_msg = "This is a short message"
    chunks = chunk_message(short_msg, max_length=100)

    assert len(chunks) == 1
    assert chunks[0] == short_msg


def test_chunk_message_long():
    """Test chunking long message."""
    long_msg = "a" * 5000
    chunks = chunk_message(long_msg, max_length=1500)

    assert len(chunks) > 1
    # Check chunk indicators
    assert "(1/" in chunks[0]
    assert f"({len(chunks)}/{len(chunks)})" in chunks[-1]


def test_format_prediction_response(normal_values):
    """Test prediction response formatting."""
    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()
    rag = MedicalRAGEngine()

    scaling_result = scaler.scale_all(normal_values)
    prediction = predictor.predict(scaling_result["scaled_values"], normal_values)
    references = rag.retrieve_references(prediction["prediction"])

    formatted = format_prediction_response(
        prediction,
        scaling_result["warnings"],
        references
    )

    assert "Prediction:" in formatted
    assert "Confidence:" in formatted
    assert "Next Steps:" in formatted
    assert "Disclaimer:" in formatted


# ---------------------------
# Integration Tests
# ---------------------------

def test_full_pipeline_normal(normal_values):
    """Test full prediction pipeline with normal values."""
    parser = BiomarkerInputParser()
    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()
    rag = MedicalRAGEngine()

    # Parse input
    json_input = json.dumps(normal_values)
    parsed, errors = parser.parse(json_input)
    assert parsed is not None

    # Scale biomarkers
    scaling_result = scaler.scale_all(parsed)
    assert len(scaling_result["warnings"]) == 0

    # Make prediction
    prediction = predictor.predict(
        scaling_result["scaled_values"],
        parsed
    )
    assert prediction["prediction"] == "normal"

    # Get references
    references = rag.retrieve_references(prediction["prediction"])
    assert len(references) > 0


def test_full_pipeline_sepsis(sepsis_values):
    """Test full prediction pipeline with sepsis values."""
    parser = BiomarkerInputParser()
    scaler = BiomarkerScaler()
    predictor = MediGuardPredictor()
    rag = MedicalRAGEngine()

    # Parse input
    json_input = json.dumps(sepsis_values)
    parsed, errors = parser.parse(json_input)
    assert parsed is not None

    # Scale biomarkers
    scaling_result = scaler.scale_all(parsed)
    assert len(scaling_result["warnings"]) > 0

    # Make prediction
    prediction = predictor.predict(
        scaling_result["scaled_values"],
        parsed
    )
    assert prediction["prediction"] == "sepsis"
    assert prediction["severity"] == "critical"

    # Get references
    references = rag.retrieve_references(prediction["prediction"])
    assert len(references) > 0
    assert any("sepsis" in r["title"].lower() for r in references)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
