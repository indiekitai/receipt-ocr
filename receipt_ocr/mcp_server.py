#!/usr/bin/env python3
"""
receipt-ocr MCP Server

Extract structured data from receipt images using Gemini AI.
"""

import json
import sys
from typing import Optional

from .extractor import extract, ReceiptData

try:
    from fastmcp import FastMCP
    mcp = FastMCP("receipt-ocr")
    HAS_MCP = True
except ImportError:
    HAS_MCP = False
    class DummyMCP:
        def tool(self):
            def decorator(f):
                return f
            return decorator
    mcp = DummyMCP()


@mcp.tool()
def receipt_extract(
    image_path: str,
    reference_date: Optional[str] = None,
) -> str:
    """
    Extract structured data from a receipt image.
    
    Uses Gemini AI to extract date, amount, vendor, and category.
    
    Args:
        image_path: Path to receipt image file or URL
        reference_date: Expected date context (YYYY-MM) for year inference
    
    Returns:
        JSON with: receipt_date, amount (cents), vendor_name, category_name
    
    Requires GEMINI_API_KEY environment variable.
    """
    try:
        result = extract(
            image_path,
            reference_date=reference_date,
        )
        
        return json.dumps({
            "success": True,
            "receipt_date": result.receipt_date,
            "amount_cents": result.amount,
            "amount_dollars": result.amount_dollars,
            "vendor_name": result.vendor_name,
            "category": result.category_name,
            "payment_method": {0: "credit", 1: "debit"}.get(result.payment_method) if result.payment_method is not None else None,
        }, ensure_ascii=False, indent=2)
        
    except FileNotFoundError:
        return json.dumps({"error": f"File not found: {image_path}"})
    except ValueError as e:
        return json.dumps({"error": str(e)})
    except Exception as e:
        return json.dumps({"error": str(e), "hint": "Ensure GEMINI_API_KEY is set"})


@mcp.tool()
def receipt_batch_extract(
    image_paths: str,
    reference_date: Optional[str] = None,
) -> str:
    """
    Extract data from multiple receipt images.
    
    Args:
        image_paths: Comma-separated paths or URLs to receipt images
        reference_date: Expected date context (YYYY-MM) for year inference
    
    Returns:
        JSON array of extraction results
    """
    paths = [p.strip() for p in image_paths.split(",")]
    results = []
    
    for path in paths:
        try:
            result = extract(path, reference_date=reference_date)
            results.append({
                "path": path,
                "success": True,
                "receipt_date": result.receipt_date,
                "amount_cents": result.amount,
                "amount_dollars": result.amount_dollars,
                "vendor_name": result.vendor_name,
                "category": result.category_name,
            })
        except Exception as e:
            results.append({
                "path": path,
                "success": False,
                "error": str(e),
            })
    
    return json.dumps({
        "total": len(results),
        "success_count": sum(1 for r in results if r.get("success")),
        "results": results,
    }, ensure_ascii=False, indent=2)


def main():
    if not HAS_MCP:
        print("Error: fastmcp not installed.", file=sys.stderr)
        print("Install with: pip install fastmcp", file=sys.stderr)
        sys.exit(1)
    mcp.run()


if __name__ == "__main__":
    main()
