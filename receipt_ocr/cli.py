"""
Command-line interface for receipt-ocr
"""

import argparse
import json
import sys

from .extractor import extract
from .client import set_api_key


def main():
    parser = argparse.ArgumentParser(
        description="Extract structured data from receipt images using Gemini AI"
    )
    parser.add_argument(
        "image",
        help="Path to receipt image or URL",
    )
    parser.add_argument(
        "--api-key",
        help="Gemini API key (or set GEMINI_API_KEY env var)",
    )
    parser.add_argument(
        "--reference-date",
        help="Expected date context (YYYY-MM) for year inference",
    )
    parser.add_argument(
        "--model",
        default="gemini-2.0-flash",
        help="Gemini model to use (default: gemini-2.0-flash)",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Include raw AI response in output",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty print JSON output",
    )

    args = parser.parse_args()

    if args.api_key:
        set_api_key(args.api_key)

    try:
        result = extract(
            args.image,
            reference_date=args.reference_date,
            model=args.model,
        )
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {args.image}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    output = result.to_dict()
    if args.raw:
        output["raw_response"] = result.raw_response

    if args.pretty:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()
