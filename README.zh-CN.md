[English](README.md) | [中文](README.zh-CN.md)

# receipt-ocr

使用 Gemini AI 从收据图片中提取结构化数据。

## 特性

- 📷 从收据图片提取日期、金额、商家、类别
- 🚀 使用 Gemini Flash，快速且低成本
- 🎯 常见收据格式准确率约 95%
- 🔧 提供 CLI 和 Python API

## 安装

```bash
pip install gemini-receipt-ocr
```

## 快速开始

### CLI

```bash
# 设置 API key
export GEMINI_API_KEY=your_api_key

# 从图片提取
receipt-ocr receipt.jpg

# 美化输出
receipt-ocr receipt.jpg --pretty

# 从 URL 提取
receipt-ocr https://example.com/receipt.jpg
```

输出：
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

# 设置 API key（或使用 GEMINI_API_KEY 环境变量）
set_api_key("your_api_key")

# 从文件提取
result = extract("receipt.jpg")
print(result.amount_dollars)  # 45.99
print(result.vendor_name)     # "Whole Foods Market"
print(result.receipt_date)    # "2025-01-15"

# 从 URL 提取
result = extract("https://example.com/receipt.jpg")

# 从 bytes 提取
with open("receipt.jpg", "rb") as f:
    result = extract(f.read())

# 带日期上下文（帮助推断年份）
result = extract("receipt.jpg", reference_date="2025-01")
```

## 输出字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `receipt_date` | str | 日期，YYYY-MM-DD 格式 |
| `amount` | int | 总金额（分） |
| `amount_dollars` | float | 总金额（美元） |
| `category` | int | 0=杂货，1=加油站，2=其他 |
| `category_name` | str | 可读的类别名 |
| `vendor_name` | str | 商家/店铺名 |
| `payment_method` | int | 0=信用卡，1=借记卡，null=未知 |

## CLI 选项

```
receipt-ocr [OPTIONS] IMAGE

参数:
  IMAGE                 收据图片路径或 URL

选项:
  --api-key TEXT        Gemini API key
  --reference-date TEXT 预期日期（YYYY-MM），用于年份推断
  --model TEXT          Gemini 模型（默认: gemini-2.0-flash）
  --raw                 包含 AI 原始响应
  --pretty              美化输出 JSON
```

## 准确率

在约 1000 张收据上的测试结果：

| 字段 | 准确率 |
|------|--------|
| 金额 | ~98% |
| 日期 | ~95% |
| 商家 | ~90% |

提升准确率的建议：
- 拍照清晰、光线充足
- 确保总金额在画面内
- 避免严重阴影/反光

## 成本

使用 Gemini Flash：每张收据约 $0.001

## License

MIT
