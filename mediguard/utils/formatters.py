"""
Response Formatters Module
Formats prediction responses for WhatsApp display.
"""

from typing import Dict, List, Any


def format_prediction_response(
    prediction_result: Dict[str, Any],
    warnings: List[str],
    references: List[Dict[str, str]]
) -> str:
    """
    Format a complete prediction response for WhatsApp.

    Args:
        prediction_result: Result from MediGuardPredictor.predict()
        warnings: List of warning messages from scaling
        references: List of medical references from RAG engine

    Returns:
        Formatted WhatsApp message string
    """
    message_parts = []

    # Header
    severity_emoji = {
        "critical": "🚨",
        "high": "⚠️",
        "moderate": "ℹ️",
        "low": "✅",
    }
    emoji = severity_emoji.get(prediction_result["severity"], "ℹ️")

    message_parts.append(f"{emoji} *MediGuard AI Prediction*\n")

    # Prediction
    message_parts.append(
        f"*Prediction:* {prediction_result['prediction_name']}\n"
        f"*Confidence:* {prediction_result['confidence']*100:.1f}%\n"
        f"*Severity:* {prediction_result['severity'].upper()}\n"
    )

    # Probability breakdown
    message_parts.append("\n*📊 Probability Breakdown:*")
    for disease_id, prob in list(prediction_result["probabilities"].items())[:5]:
        if prob > 0.01:  # Only show probabilities > 1%
            disease_name = disease_id.replace("_", " ").title()
            bar = "█" * int(prob * 20)  # Bar chart
            message_parts.append(f"  {disease_name}: {prob*100:.1f}% {bar}")

    # Key biomarkers
    if prediction_result["key_biomarkers"]:
        message_parts.append("\n*🔬 Key Biomarkers:*")
        for kb in prediction_result["key_biomarkers"][:5]:
            message_parts.append(
                f"  {kb['direction']} {kb['code']}: {kb['value']} {kb['unit']} "
                f"({kb['status']})"
            )

    # Explanation
    message_parts.append(f"\n*💡 Explanation:*\n{prediction_result['explanation']}")

    # Warnings
    if warnings:
        message_parts.append("\n*⚠️ Warnings:*")
        # Group warnings by severity
        critical_warnings = [w for w in warnings if "🚨" in w or "CRITICAL" in w]
        other_warnings = [w for w in warnings if w not in critical_warnings]

        for w in critical_warnings[:5]:  # Limit to 5 critical
            message_parts.append(f"  {w}")
        for w in other_warnings[:3]:  # Limit to 3 other
            message_parts.append(f"  {w}")

        if len(warnings) > 8:
            message_parts.append(f"  ... and {len(warnings) - 8} more warnings")

    # References
    if references:
        message_parts.append("\n*📚 References:*")
        for i, ref in enumerate(references[:3], 1):
            message_parts.append(
                f"{i}. {ref['title']} — {ref['section']}\n"
                f"   _{ref['citation']}_"
            )

    # Next steps
    message_parts.append(
        "\n*Next Steps:*\n"
        "• Review findings with a qualified healthcare provider\n"
        "• For critical findings, seek immediate medical attention\n"
        "• Type 'explain more' for detailed analysis\n"
        "• Type 'show sources' for full references"
    )

    # Disclaimer
    message_parts.append(
        "\n_⚕️ Disclaimer: This AI-powered analysis is for informational purposes "
        "only and does not replace professional medical advice. Always consult "
        "a healthcare provider for medical decisions._"
    )

    return "\n".join(message_parts)


def format_biomarker_summary(raw_summary: Dict[str, Any]) -> str:
    """
    Format biomarker summary for user review.

    Args:
        raw_summary: Raw biomarker summary from scaler

    Returns:
        Formatted string
    """
    message_parts = ["*📋 Biomarker Summary:*\n"]

    # Group by category
    categories = {}
    for bio_id, info in raw_summary.items():
        # Get category from biomarker data (would need to pass this)
        # For now, simple formatting
        categories.setdefault("All", []).append(info)

    for bio_info in sorted(raw_summary.values(), key=lambda x: x["name"]):
        raw_val = bio_info["raw_value"]
        unit = bio_info["unit"]
        name = bio_info["name"]
        code = bio_info["code"]
        normal = bio_info["normal_range"]

        # Status indicator
        if raw_val < normal["min"]:
            status = "↓"
        elif raw_val > normal["max"]:
            status = "↑"
        else:
            status = "→"

        message_parts.append(
            f"{status} {code}: {raw_val} {unit} "
            f"(normal: {normal['min']}-{normal['max']})"
        )

    return "\n".join(message_parts)


def format_help_message() -> str:
    """Format help message for MediGuard bot."""
    return """*MediGuard AI - Clinical Triage Assistant*

*How to Submit Blood Test Values:*

*Option 1: JSON Format*
```
{
  "hemoglobin": 14.5,
  "wbc_count": 7.2,
  "platelet_count": 250,
  ...
}
```

*Option 2: Key-Value Format*
```
hemoglobin=14.5, wbc_count=7.2, platelet_count=250, ...
```

*Option 3: CSV Format*
```
14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5
```

*Required Biomarkers (24 total):*
Hemoglobin, WBC Count, Platelet Count, Glucose, Creatinine, BUN, Sodium, Potassium, Chloride, Calcium, ALT, AST, Total Bilirubin, Albumin, Total Protein, LDH, Troponin, BNP, CRP, ESR, Procalcitonin, D-Dimer, INR, Lactate

*Commands:*
• `/start` - Get started
• `template` - Get input template
• `explain more` - Detailed analysis
• `show sources` - Medical references
• `help` - Show this message
• `reset` - Clear session

*⚕️ Note:* This is an AI assistant for educational and triage purposes. Always consult a healthcare provider for medical decisions.
"""


def format_template_message(format_type: str = "json") -> str:
    """
    Format template message with example values.

    Args:
        format_type: "json", "key_value", or "csv"

    Returns:
        Template message
    """
    if format_type == "json":
        return """*📋 JSON Template (copy and edit values):*

```
{
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
  "lactate": 1.5
}
```

Replace values with actual test results and send.
"""

    elif format_type == "key_value":
        return """*📋 Key-Value Template (copy and edit values):*

```
hemoglobin=14.5, wbc_count=7.2, platelet_count=250, glucose=95, creatinine=1.0, bun=15, sodium=138, potassium=4.2, chloride=102, calcium=9.5, alt=25, ast=30, bilirubin_total=0.8, albumin=4.0, total_protein=7.0, ldh=180, troponin=0.02, bnp=50, crp=1.5, esr=10, procalcitonin=0.03, d_dimer=0.3, inr=1.0, lactate=1.5
```

Replace values with actual test results and send.
"""

    else:  # CSV
        return """*📋 CSV Template (copy and edit values):*

Order: Hemoglobin, WBC, Platelet, Glucose, Creatinine, BUN, Na, K, Cl, Ca, ALT, AST, T.Bili, Albumin, T.Protein, LDH, Troponin, BNP, CRP, ESR, PCT, D-Dimer, INR, Lactate

```
14.5,7.2,250,95,1.0,15,138,4.2,102,9.5,25,30,0.8,4.0,7.0,180,0.02,50,1.5,10,0.03,0.3,1.0,1.5
```

Replace values with actual test results and send.
"""


def chunk_message(message: str, max_length: int = 4000) -> List[str]:
    """
    Split long message into WhatsApp-friendly chunks.

    Args:
        message: Full message text
        max_length: Maximum chunk size

    Returns:
        List of message chunks
    """
    if len(message) <= max_length:
        return [message]

    chunks = []
    current_chunk = ""

    for line in message.split("\n"):
        if len(current_chunk) + len(line) + 1 > max_length:
            chunks.append(current_chunk.rstrip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    if current_chunk:
        chunks.append(current_chunk.rstrip())

    # Add chunk indicators
    if len(chunks) > 1:
        return [f"({i}/{len(chunks)})\n{chunk}" for i, chunk in enumerate(chunks, 1)]

    return chunks
