"""
MediGuard AI WhatsApp Bot
Clinical triage and prediction system via WhatsApp.
"""

import os
import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client

from mediguard.models.scaler import BiomarkerScaler
from mediguard.models.predictor import MediGuardPredictor
from mediguard.parsers.input_parser import BiomarkerInputParser
from mediguard.knowledge.rag_engine import MedicalRAGEngine
from mediguard.utils.security import SecureLogger, validate_input_security, anonymize_user_id
from mediguard.utils.formatters import (
    format_prediction_response,
    format_biomarker_summary,
    format_help_message,
    format_template_message,
    chunk_message,
)


# ---------------------------
# Configuration & Initialization
# ---------------------------

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "mediguard.db")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN:
    missing = []
    if not TWILIO_ACCOUNT_SID:
        missing.append("TWILIO_ACCOUNT_SID")
    if not TWILIO_AUTH_TOKEN:
        missing.append("TWILIO_AUTH_TOKEN")
    raise RuntimeError(
        f"Missing required environment variables: {', '.join(missing)}. Set them in .env."
    )

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = Flask(__name__)

# Initialize MediGuard components
scaler = BiomarkerScaler()
predictor = MediGuardPredictor()
parser = BiomarkerInputParser()
rag_engine = MedicalRAGEngine()
secure_logger = SecureLogger(DB_PATH)


# ---------------------------
# Database Helpers
# ---------------------------

def get_db_connection() -> sqlite3.Connection:
    """Get database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize database tables."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            user_id TEXT PRIMARY KEY,
            mode TEXT DEFAULT 'idle',
            last_prediction TEXT,
            last_references TEXT,
            pending_confirmation INTEGER DEFAULT 0,
            pending_values TEXT,
            updated_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()

    # Initialize secure logging tables
    secure_logger._init_db()


def get_session(user_id: str) -> sqlite3.Row:
    """Get or create user session."""
    conn = get_db_connection()
    cur = conn.execute("SELECT * FROM sessions WHERE user_id=?", (user_id,))
    row = cur.fetchone()

    if row is None:
        conn.execute(
            "INSERT INTO sessions (user_id, updated_at) VALUES (?, ?)",
            (user_id, datetime.utcnow().isoformat()),
        )
        conn.commit()
        cur = conn.execute("SELECT * FROM sessions WHERE user_id=?", (user_id,))
        row = cur.fetchone()

    conn.close()
    assert row is not None
    return row


def update_session(user_id: str, **kwargs: Any) -> None:
    """Update session data."""
    if not kwargs:
        return

    columns = ", ".join([f"{k}=?" for k in kwargs.keys()])
    values = list(kwargs.values())
    values.extend([datetime.utcnow().isoformat(), user_id])

    conn = get_db_connection()
    conn.execute(
        f"UPDATE sessions SET {columns}, updated_at=? WHERE user_id=?",
        values,
    )
    conn.commit()
    conn.close()


# ---------------------------
# Bot Logic
# ---------------------------

def handle_message(user_id: str, text: str) -> str:
    """
    Main message handler for MediGuard bot.

    Args:
        user_id: WhatsApp user ID
        text: Message text from user

    Returns:
        Response message
    """
    # Security validation
    is_valid, error_msg = validate_input_security(text)
    if not is_valid:
        secure_logger.audit("security_violation", user_id, {"reason": error_msg})
        return f"⚠️ Security error: {error_msg}"

    text_lower = text.lower().strip()

    # Log incoming message
    secure_logger.log_event(
        user_id,
        "message_received",
        {"event_type": "user_message", "timestamp": datetime.utcnow().isoformat()},
    )

    # Commands
    if text_lower in ["/start", "start", "hello", "hi"]:
        return handle_start()

    if text_lower in ["help", "/help"]:
        return format_help_message()

    if text_lower in ["template", "get template", "show template"]:
        return handle_template_request(text_lower)

    if text_lower in ["reset", "/reset", "clear"]:
        return handle_reset(user_id)

    if "explain more" in text_lower:
        return handle_explain_more(user_id)

    if "show sources" in text_lower or "references" in text_lower:
        return handle_show_sources(user_id)

    # Try to parse biomarker input
    parsed_values, parse_errors = parser.parse(text)

    if parsed_values is not None:
        # Successfully parsed biomarker values
        return handle_prediction_request(user_id, parsed_values)

    # If parsing failed, check if it's a query
    if len(text.strip()) > 10:
        return handle_query(text)

    # Default fallback
    return (
        "I didn't understand that. Send blood test values in JSON, key=value, or CSV format.\n\n"
        "Type 'help' for instructions or 'template' for an example."
    )


def handle_start() -> str:
    """Handle /start command."""
    return """*Welcome to MediGuard AI! 🏥*

I'm your clinical triage assistant powered by AI. Send me blood test results and I'll provide:

• Disease prediction & confidence
• Key biomarker analysis
• Medical references
• Risk assessment

*Get started:*
Type 'template' to see input format
Type 'help' for full instructions

_⚕️ This is an AI assistant for educational/triage purposes. Always consult a healthcare provider for medical decisions._
"""


def handle_template_request(text: str) -> str:
    """Handle template request."""
    if "key" in text or "value" in text:
        return format_template_message("key_value")
    elif "csv" in text:
        return format_template_message("csv")
    else:
        return format_template_message("json")


def handle_reset(user_id: str) -> str:
    """Handle reset command."""
    update_session(
        user_id,
        mode="idle",
        last_prediction=None,
        last_references=None,
        pending_confirmation=0,
        pending_values=None,
    )
    secure_logger.audit("session_reset", user_id)
    return "✅ Session cleared. Send new biomarker values or type 'help'."


def handle_prediction_request(user_id: str, biomarker_values: Dict[str, float]) -> str:
    """
    Handle prediction request with parsed biomarker values.

    Args:
        user_id: User ID
        biomarker_values: Parsed biomarker values

    Returns:
        Formatted prediction response
    """
    try:
        # Scale biomarkers
        scaling_result = scaler.scale_all(biomarker_values)
        scaled_values = scaling_result["scaled_values"]
        warnings = scaling_result["warnings"]
        raw_summary = scaling_result["raw_summary"]

        # Make prediction
        prediction_result = predictor.predict(scaled_values, biomarker_values)

        # Retrieve medical references
        references = rag_engine.retrieve_references(
            prediction_result["prediction"],
            max_results=3
        )

        # Store in session for follow-up queries
        update_session(
            user_id,
            mode="reviewed",
            last_prediction=json.dumps(prediction_result),
            last_references=json.dumps(references),
        )

        # Log prediction (anonymized, no PHI)
        secure_logger.log_event(
            user_id,
            "prediction_generated",
            {
                "prediction": prediction_result["prediction"],
                "confidence": prediction_result["confidence"],
                "severity": prediction_result["severity"],
                "num_biomarkers": len(biomarker_values),
                "num_warnings": len(warnings),
            },
        )

        # Format response
        response = format_prediction_response(
            prediction_result,
            warnings,
            references
        )

        return response

    except Exception as e:
        secure_logger.audit("prediction_error", user_id, {"error": str(e)})
        return f"❌ Error processing prediction: {str(e)}\n\nPlease check your input format and try again."


def handle_explain_more(user_id: str) -> str:
    """Handle 'explain more' request."""
    sess = get_session(user_id)

    if not sess["last_prediction"]:
        return "No recent prediction to explain. Please submit biomarker values first."

    try:
        prediction_result = json.loads(sess["last_prediction"])

        explanation = f"*🔍 Detailed Analysis*\n\n"
        explanation += f"*Prediction:* {prediction_result['prediction_name']}\n"
        explanation += f"*Confidence:* {prediction_result['confidence']*100:.1f}%\n"
        explanation += f"*Severity Level:* {prediction_result['severity'].upper()}\n\n"

        explanation += f"*Full Explanation:*\n{prediction_result['explanation']}\n\n"

        # Detailed biomarker breakdown
        if prediction_result["key_biomarkers"]:
            explanation += "*Detailed Biomarker Analysis:*\n"
            for kb in prediction_result["key_biomarkers"]:
                explanation += (
                    f"\n{kb['direction']} *{kb['name']} ({kb['code']})*\n"
                    f"  Value: {kb['value']} {kb['unit']}\n"
                    f"  Status: {kb['status']}\n"
                    f"  Deviation: {kb['deviation']*100:.0f}% from normal\n"
                )

        # All probabilities
        explanation += "\n*All Disease Probabilities:*\n"
        for disease_id, prob in prediction_result["probabilities"].items():
            disease_name = disease_id.replace("_", " ").title()
            explanation += f"  {disease_name}: {prob*100:.1f}%\n"

        return explanation

    except Exception as e:
        return f"❌ Error generating explanation: {str(e)}"


def handle_show_sources(user_id: str) -> str:
    """Handle 'show sources' request."""
    sess = get_session(user_id)

    if not sess["last_references"]:
        return "No references available. Please submit biomarker values first."

    try:
        references = json.loads(sess["last_references"])
        return rag_engine.format_references(references)

    except Exception as e:
        return f"❌ Error retrieving sources: {str(e)}"


def handle_query(query_text: str) -> str:
    """
    Handle general medical query using RAG.

    Args:
        query_text: User's natural language query

    Returns:
        Response with relevant references
    """
    try:
        references = rag_engine.query(query_text)

        if not references:
            return (
                "I couldn't find specific references for that query. "
                "I'm primarily designed for blood test analysis.\n\n"
                "Send biomarker values or type 'help' for instructions."
            )

        response = f"*📚 References for: \"{query_text[:50]}...\"*\n\n"
        response += rag_engine.format_references(references)

        return response

    except Exception as e:
        return f"❌ Error processing query: {str(e)}"


# ---------------------------
# Flask Routes
# ---------------------------

@app.route("/")
def root() -> str:
    """Root endpoint."""
    return "MediGuard AI WhatsApp Bot is running. 🏥"


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    """WhatsApp webhook endpoint."""
    init_db()  # Ensure tables exist

    from_number = request.form.get("From", "")
    body = request.form.get("Body", "").strip()
    user_id = from_number or "unknown"

    # Process message
    reply_text = handle_message(user_id, body)

    # Send response (chunked if necessary)
    resp = MessagingResponse()
    chunks = chunk_message(reply_text, max_length=1500)

    for chunk in chunks:
        resp.message(chunk)

    return str(resp)


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "mediguard-bot"}, 200


# ---------------------------
# Cleanup Task (run periodically)
# ---------------------------

def cleanup_expired_logs():
    """Cleanup expired logs (should be run via cron/scheduler)."""
    deleted = secure_logger.cleanup_expired_logs()
    print(f"Cleaned up {deleted} expired log entries")


# ---------------------------
# Main Entry Point
# ---------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    init_db()
    print(f"MediGuard AI Bot starting on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
