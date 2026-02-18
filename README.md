# receipt-ocr

Extract structured data from receipt images using Gemini AI.

## Features

- 📷 Extract date, amount, vendor, category from receipt images
- 🚀 Fast and cheap with Gemini Flash
- 🎯 ~95% accuracy on common receipt formats
- 🔧 CLI and Python API

## Installation

```bash
pip install gemini-receipt-ocr
```

## Quick Start

### CLI

```bash
# Set API key
export GEMINI_API_KEY=your_api_key

# Extract from image
receipt-ocr receipt.jpg

# Pretty print
receipt-ocr receipt.jpg --pretty

# From URL
receipt-ocr https://example.com/receipt.jpg
```

Output:
```json
{
  "receipt_date": "2025-01-15",
  "amount": 4599,
  "amount_dollars": 45.99,
  "category": 0,
  "category_name": "grocery",
  "vendor_name": "Whole Foods Market",
  "payment_method": 0
}
```

### Python API

```python
from receipt_ocr import extract, set_api_key

# Set API key (or use GEMINI_API_KEY env var)
set_api_key("your_api_key")

# Extract from file
result = extract("receipt.jpg")
print(result.amount_dollars)  # 45.99
print(result.vendor_name)     # "Whole Foods Market"
print(result.receipt_date)    # "2025-01-15"

# Extract from URL
result = extract("https://example.com/receipt.jpg")

# Extract from bytes
with open("receipt.jpg", "rb") as f:
    result = extract(f.read())

# With date context (helps infer year)
result = extract("receipt.jpg", reference_date="2025-01")
```

## Output Fields

| Field | Type | Description |
|-------|------|-------------|
| `receipt_date` | str | Date in YYYY-MM-DD format |
| `amount` | int | Total amount in cents |
| `amount_dollars` | float | Total amount in dollars |
| `category` | int | 0=grocery, 1=gas station, 2=other |
| `category_name` | str | Human-readable category |
| `vendor_name` | str | Merchant/store name |
| `payment_method` | int | 0=credit, 1=debit, null=unknown |

## CLI Options

```
receipt-ocr [OPTIONS] IMAGE

Arguments:
  IMAGE                 Path to receipt image or URL

Options:
  --api-key TEXT        Gemini API key
  --reference-date TEXT Expected date (YYYY-MM) for year inference
  --model TEXT          Gemini model (default: gemini-2.0-flash)
  --raw                 Include raw AI response
  --pretty              Pretty print JSON
```

## Accuracy

Tested on ~1000 receipts:

| Field | Accuracy |
|-------|----------|
| Amount | ~98% |
| Date | ~95% |
| Vendor | ~90% |

Tips for better accuracy:
- Clear, well-lit photos
- Include the total amount in frame
- Avoid heavy shadows/glare

## Cost

Using Gemini Flash: ~$0.001 per receipt

## License

MIT
