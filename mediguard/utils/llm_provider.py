"""
Groq LLM Provider - Centralized client with retry logic and caching.

Features:
- Singleton client initialization
- Exponential backoff for rate limits (429)
- Vision/OCR support via base64
- Structured JSON output
- Backward compatibility alias
"""

import os
import time
import base64
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# =============================================================================
# Configuration
# =============================================================================

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TEXT_MODEL = os.getenv("GROQ_TEXT_MODEL", "llama-3.3-70b-versatile")
GROQ_VISION_MODEL = os.getenv("GROQ_VISION_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
GROQ_JSON_MODEL = os.getenv("GROQ_JSON_MODEL", "llama-3.3-70b-versatile")
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.5"))
MAX_RETRIES = int(os.getenv("GROQ_MAX_RETRIES", "3"))

# =============================================================================
# Client Initialization
# =============================================================================

_client = None
GROQ_AVAILABLE = False

try:
    from groq import Groq
    if GROQ_API_KEY:
        _client = Groq(api_key=GROQ_API_KEY)
        GROQ_AVAILABLE = True
        logger.info("[GROQ] Client initialized successfully")
    else:
        logger.warning("[GROQ] API key not configured")
except ImportError:
    logger.warning("[GROQ] SDK not installed. Install with: pip install groq")
except Exception as e:
    logger.error(f"[GROQ] Initialization failed: {e}")


# =============================================================================
# Retry Decorator
# =============================================================================

def _retry_with_backoff(func):
    """Decorator for exponential backoff on 429/5xx errors."""
    def wrapper(*args, **kwargs):
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                status = getattr(e, 'status_code', None)
                if status in (429, 500, 502, 503) and attempt < MAX_RETRIES - 1:
                    delay = 2 ** attempt
                    logger.warning(f"[GROQ] Retry {attempt + 1}/{MAX_RETRIES} in {delay}s (status {status})")
                    time.sleep(delay)
                    continue
                raise
        if last_error:
            raise last_error
        return None
    return wrapper


# =============================================================================
# Public API Functions
# =============================================================================

def get_client():
    """Get the Groq client instance."""
    return _client


def is_available() -> bool:
    """Check if Groq API is available."""
    return GROQ_AVAILABLE


@_retry_with_backoff
def generate_text(
    prompt: str,
    temperature: Optional[float] = None,
    max_tokens: int = 4096,
    system_prompt: Optional[str] = None,
) -> Optional[str]:
    """
    Generate text using Groq LLM.
    
    Args:
        prompt: User prompt
        temperature: Optional temperature (0.0-2.0)
        max_tokens: Maximum tokens in response
        system_prompt: Optional system prompt
        
    Returns:
        Generated text or None
    """
    if not GROQ_AVAILABLE or not _client:
        logger.warning("[GROQ] generate_text called but client unavailable")
        return None
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    response = _client.chat.completions.create(
        messages=messages,
        model=GROQ_TEXT_MODEL,
        temperature=temperature if temperature is not None else TEMPERATURE,
        max_tokens=max_tokens,
    )
    
    result = response.choices[0].message.content
    logger.debug(f"[GROQ] Text generation: {len(result or '')} chars")
    return result


@_retry_with_backoff
def generate_with_image(
    prompt: str,
    image_path: str,
    temperature: Optional[float] = None,
    max_tokens: int = 4096,
) -> Optional[str]:
    """
    Generate text with image input using Groq Vision.
    
    Args:
        prompt: Text prompt
        image_path: Path to image file
        temperature: Optional temperature
        max_tokens: Maximum tokens
        
    Returns:
        Generated text or None
    """
    if not GROQ_AVAILABLE or not _client:
        logger.warning("[GROQ] generate_with_image called but client unavailable")
        return None
    
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    if not path.is_file():
        raise ValueError(f"Not a file: {image_path}")
    
    # Check file size (max 20MB)
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError(f"Image too large: {path.stat().st_size / 1024 / 1024:.1f}MB (max 20MB)")
    
    # Read and encode
    with open(path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Determine MIME type
    mime_map = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
        '.bmp': 'image/bmp',
    }
    mime_type = mime_map.get(path.suffix.lower(), 'image/png')
    
    response = _client.chat.completions.create(
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{image_data}"
                    }
                }
            ]
        }],
        model=GROQ_VISION_MODEL,
        temperature=temperature if temperature is not None else TEMPERATURE,
        max_tokens=max_tokens,
    )
    
    result = response.choices[0].message.content
    logger.debug(f"[GROQ] Vision generation: {len(result or '')} chars")
    return result


@_retry_with_backoff
def generate_json(
    prompt: str,
    schema: Dict[str, Any],
    temperature: Optional[float] = None,
) -> Optional[Dict[str, Any]]:
    """
    Generate structured JSON output.
    
    Args:
        prompt: Extraction prompt
        schema: JSON schema for output
        temperature: Optional temperature (lower = more deterministic)
        
    Returns:
        Parsed JSON dict or None
    """
    if not GROQ_AVAILABLE or not _client:
        logger.warning("[GROQ] generate_json called but client unavailable")
        return None
    
    try:
        response = _client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Respond with valid JSON only. No explanations."},
                {"role": "user", "content": prompt}
            ],
            model=GROQ_JSON_MODEL,
            temperature=temperature if temperature is not None else 0.3,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "extraction_result",
                    "strict": False,
                    "schema": schema,
                }
            },
        )
        
        content = response.choices[0].message.content
        if not content:
            return None
        
        result = json.loads(content)
        logger.debug("[GROQ] JSON generation successful")
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"[GROQ] JSON parse error: {e}")
        return None


# =============================================================================
# Backward Compatibility
# =============================================================================

def gemini_generate_text(prompt: str, temperature: float = 0.5) -> Optional[str]:
    """Backward compatibility alias for generate_text."""
    return generate_text(prompt, temperature=temperature)
