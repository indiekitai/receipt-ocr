"""
receipt-ocr: Extract structured data from receipt images using Gemini AI
"""

from .extractor import extract, extract_from_url, ReceiptData
from .client import set_api_key, get_client

__version__ = "0.1.0"
__all__ = ["extract", "extract_from_url", "ReceiptData", "set_api_key", "get_client"]
