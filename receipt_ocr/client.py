"""
Gemini client management
"""

import os
from google import genai

_client = None
_api_key = None

DEFAULT_MODEL = "gemini-2.0-flash"


def set_api_key(api_key: str):
    """Set the Gemini API key"""
    global _api_key, _client
    _api_key = api_key
    _client = None  # Reset client to use new key


def get_api_key() -> str:
    """Get API key from explicit setting or environment"""
    if _api_key:
        return _api_key
    return os.environ.get("GEMINI_API_KEY", "")


def get_client() -> genai.Client:
    """Get or create Gemini client"""
    global _client
    if _client is None:
        api_key = get_api_key()
        if not api_key:
            raise ValueError(
                "Gemini API key not set. Use set_api_key() or set GEMINI_API_KEY environment variable."
            )
        _client = genai.Client(api_key=api_key)
    return _client
