"""
Core receipt extraction logic
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import requests
from google.genai import types

from .client import get_client, DEFAULT_MODEL


@dataclass
class ReceiptData:
    """Extracted receipt data"""
    receipt_date: Optional[str] = None  # YYYY-MM-DD
    amount: Optional[int] = None  # Amount in cents
    category: Optional[int] = None  # 0=grocery, 1=gas, 2=other
    vendor_name: Optional[str] = None
    payment_method: Optional[int] = None  # 0=credit, 1=debit
    raw_response: Optional[str] = None  # Original AI response

    @property
    def amount_dollars(self) -> Optional[float]:
        """Amount in dollars"""
        if self.amount is None:
            return None
        return self.amount / 100

    @property
    def category_name(self) -> Optional[str]:
        """Human-readable category"""
        if self.category is None:
            return None
        return {0: "grocery", 1: "gas_station", 2: "other"}.get(self.category, "unknown")

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "receipt_date": self.receipt_date,
            "amount": self.amount,
            "amount_dollars": self.amount_dollars,
            "category": self.category,
            "category_name": self.category_name,
            "vendor_name": self.vendor_name,
            "payment_method": self.payment_method,
        }


def _get_prompt(reference_date: Optional[str] = None) -> str:
    """Generate the extraction prompt"""
    if reference_date:
        date_hint = f"This receipt is expected to be from around {reference_date}. Use this to infer the year if not shown."
    else:
        current_year = datetime.now().year
        date_hint = f"If the year is not shown on the receipt, assume it is {current_year}."

    return f"""
Analyze this receipt/invoice image and extract the following information in JSON format:

{{
    "receipt_date": "YYYY-MM-DD format date",
    "amount": total amount in cents (e.g., $15.68 returns 1568),
    "category": category type (0=supermarket/grocery/food, 1=gas station, 2=other),
    "vendor_name": "merchant/vendor name",
    "payment_method": payment method (0=credit card, 1=debit card, null=cannot determine)
}}

{date_hint}

Rules:
- If a field cannot be identified, return null
- For amount: Extract the TOTAL amount (including tax), NOT subtotal. Convert to cents (multiply dollars by 100)
- For receipt_date: Use the transaction/purchase date shown on the receipt
- For category: Use 0 for grocery stores, supermarkets, food suppliers; 1 for gas stations; 2 for everything else
- Return ONLY the JSON object, no other text
"""


def _parse_response(response_text: str) -> dict:
    """Parse Gemini response to JSON"""
    text = response_text.strip()
    
    # Clean markdown code blocks
    if text.startswith("```json"):
        text = text[7:]
    if text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Fallback: extract JSON with regex
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            return json.loads(match.group())
        raise ValueError(f"Failed to parse response: {response_text}")


def _get_mime_type(file_path: str) -> str:
    """Determine MIME type from file extension"""
    ext = Path(file_path).suffix.lower()
    mime_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mime_types.get(ext, "image/jpeg")


def extract(
    image: Union[str, bytes, Path],
    reference_date: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> ReceiptData:
    """
    Extract receipt data from an image.

    Args:
        image: File path, URL, or bytes of the receipt image
        reference_date: Expected date context (YYYY-MM format) for year inference
        model: Gemini model to use

    Returns:
        ReceiptData object with extracted fields
    """
    # Load image bytes
    if isinstance(image, bytes):
        image_bytes = image
        mime_type = "image/jpeg"
    elif isinstance(image, (str, Path)):
        path = str(image)
        if path.startswith(("http://", "https://")):
            return extract_from_url(path, reference_date, model)
        with open(path, "rb") as f:
            image_bytes = f.read()
        mime_type = _get_mime_type(path)
    else:
        raise TypeError(f"Unsupported image type: {type(image)}")

    # Call Gemini
    client = get_client()
    prompt = _get_prompt(reference_date)

    response = client.models.generate_content(
        model=model,
        contents=[
            prompt,
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
        ],
    )

    # Parse response
    raw_text = response.text
    data = _parse_response(raw_text)

    return ReceiptData(
        receipt_date=data.get("receipt_date"),
        amount=data.get("amount"),
        category=data.get("category"),
        vendor_name=data.get("vendor_name"),
        payment_method=data.get("payment_method"),
        raw_response=raw_text,
    )


def extract_from_url(
    url: str,
    reference_date: Optional[str] = None,
    model: str = DEFAULT_MODEL,
) -> ReceiptData:
    """
    Extract receipt data from an image URL.

    Args:
        url: URL of the receipt image
        reference_date: Expected date context (YYYY-MM format)
        model: Gemini model to use

    Returns:
        ReceiptData object with extracted fields
    """
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    
    # Determine mime type from content-type header or URL
    content_type = response.headers.get("content-type", "")
    if "jpeg" in content_type or "jpg" in content_type:
        mime_type = "image/jpeg"
    elif "png" in content_type:
        mime_type = "image/png"
    elif "webp" in content_type:
        mime_type = "image/webp"
    else:
        mime_type = _get_mime_type(url)

    # Call Gemini
    client = get_client()
    prompt = _get_prompt(reference_date)

    resp = client.models.generate_content(
        model=model,
        contents=[
            prompt,
            types.Part.from_bytes(data=response.content, mime_type=mime_type),
        ],
    )

    raw_text = resp.text
    data = _parse_response(raw_text)

    return ReceiptData(
        receipt_date=data.get("receipt_date"),
        amount=data.get("amount"),
        category=data.get("category"),
        vendor_name=data.get("vendor_name"),
        payment_method=data.get("payment_method"),
        raw_response=raw_text,
    )
