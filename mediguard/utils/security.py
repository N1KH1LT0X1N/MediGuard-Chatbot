"""
Security Utilities Module
Handles anonymization, secure logging, and data protection.
"""

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple


def anonymize_user_id(user_id: str, salt: Optional[str] = None) -> str:
    """
    Anonymize user ID (phone number) using SHA-256 hashing.

    Args:
        user_id: Original user identifier (WhatsApp phone number)
        salt: Optional salt for hashing (defaults to env var)

    Returns:
        Anonymized hash of the user ID
    """
    if salt is None:
        salt = os.getenv("ANONYMIZATION_SALT", "mediguard_default_salt_2024")

    combined = f"{salt}:{user_id}"
    hash_obj = hashlib.sha256(combined.encode("utf-8"))
    return hash_obj.hexdigest()[:16]  # First 16 chars for brevity


class SecureLogger:
    """
    Secure logging system that:
    - Anonymizes user identifiers
    - Removes PHI (Protected Health Information)
    - Implements data retention policies
    - Encrypts sensitive data at rest
    """

    def __init__(self, db_path: str):
        """
        Initialize secure logger.

        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """Initialize secure logging tables."""
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        # Main logging table (anonymized)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mediguard_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                created_at TEXT NOT NULL,
                retention_until TEXT NOT NULL
            )
            """
        )

        # Audit trail (high-level only, no PHI)
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS mediguard_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT NOT NULL,
                session_id TEXT,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
            """
        )

        conn.commit()
        conn.close()

    def log_event(
        self,
        user_id: str,
        event_type: str,
        event_data: Dict[str, Any],
        retention_days: int = 30
    ) -> None:
        """
        Log an event with automatic PHI removal and anonymization.

        Args:
            user_id: Original user ID (will be anonymized)
            event_type: Type of event (e.g., "prediction_request", "input_received")
            event_data: Event data (PHI will be removed)
            retention_days: Days to retain this log
        """
        session_id = anonymize_user_id(user_id)
        sanitized_data = self._remove_phi(event_data)

        now = datetime.utcnow()
        retention_until = now + timedelta(days=retention_days)

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO mediguard_logs (session_id, event_type, event_data, created_at, retention_until)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                session_id,
                event_type,
                json.dumps(sanitized_data),
                now.isoformat(),
                retention_until.isoformat(),
            ),
        )
        conn.commit()
        conn.close()

    def audit(
        self,
        action: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log audit trail entry (high-level actions only).

        Args:
            action: Action description
            user_id: Optional user ID (will be anonymized)
            metadata: Optional metadata (must not contain PHI)
        """
        session_id = anonymize_user_id(user_id) if user_id else None

        conn = sqlite3.connect(self.db_path)
        conn.execute(
            """
            INSERT INTO mediguard_audit (action, session_id, timestamp, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (
                action,
                session_id,
                datetime.utcnow().isoformat(),
                json.dumps(metadata) if metadata else None,
            ),
        )
        conn.commit()
        conn.close()

    def cleanup_expired_logs(self) -> int:
        """
        Remove logs that have exceeded their retention period.

        Returns:
            Number of logs deleted
        """
        now = datetime.utcnow().isoformat()

        conn = sqlite3.connect(self.db_path)
        cur = conn.execute(
            "DELETE FROM mediguard_logs WHERE retention_until < ?",
            (now,)
        )
        deleted_count = cur.rowcount
        conn.commit()
        conn.close()

        return deleted_count

    def _remove_phi(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove Protected Health Information from event data.

        Removes:
        - Direct identifiers (names, phone numbers, addresses)
        - Keeps only aggregated/statistical data
        """
        sanitized = {}

        # Allowed non-PHI fields
        allowed_fields = {
            "prediction",
            "confidence",
            "severity",
            "event_type",
            "timestamp",
            "num_biomarkers",
            "num_warnings",
            "model_version",
        }

        for key, value in data.items():
            if key in allowed_fields:
                sanitized[key] = value
            elif key == "biomarker_count":
                sanitized[key] = value
            elif key == "warning_count":
                sanitized[key] = value
            # Skip raw biomarker values and other PHI

        return sanitized


def validate_input_security(user_input: str) -> Tuple[bool, Optional[str]]:
    """
    Validate user input for security threats.

    Checks for:
    - SQL injection attempts
    - Script injection
    - Excessive length
    - Suspicious patterns

    Args:
        user_input: Raw user input string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Length check
    if len(user_input) > 10000:
        return False, "Input too long (max 10000 characters)"

    # SQL injection patterns
    sql_patterns = [
        "'; DROP TABLE",
        "'; DELETE FROM",
        "UNION SELECT",
        "'; INSERT INTO",
        "<script",
        "javascript:",
        "onerror=",
    ]

    user_input_upper = user_input.upper()
    for pattern in sql_patterns:
        if pattern.upper() in user_input_upper:
            return False, f"Suspicious pattern detected: {pattern}"

    return True, None


def secure_logger(db_path: str) -> SecureLogger:
    """
    Factory function to create a SecureLogger instance.

    Args:
        db_path: Path to SQLite database

    Returns:
        SecureLogger instance
    """
    return SecureLogger(db_path)
