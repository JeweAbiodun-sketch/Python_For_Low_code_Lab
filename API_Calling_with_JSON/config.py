from typing import Any, Dict

OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 500
OPENAI_TEMPERATURE = 0.4
OPENAI_REQUEST_TIMEOUT = 15
IMAGE_FORMAT = "JPEG"
IMAGE_QUALITY = 95
PRINT_WIDTH = 60
SYSTEM_PROMPT = "You are a professional e-commerce copywriter. Return only valid JSON."
PROMPT_TEMPLATE = """Analyze this product image and create an e-commerce listing.

Product Info:
- Name: {name}
- Category: {category}
- Brand: {brand}
- Color: {color}
- Price: {price} {currency}

Return ONLY valid JSON in this format:
{{
  "title": "Attractive product title",
  "description": "Compelling 80-120 word description",
  "features": ["feature1", "feature2", "feature3"],
  "tags": ["tag1", "tag2", "tag3"]
}}
"""


def get_openai_config() -> Dict[str, Any]:
    return {
        "model": OPENAI_MODEL,
        "max_tokens": OPENAI_MAX_TOKENS,
        "temperature": OPENAI_TEMPERATURE,
        "timeout": OPENAI_REQUEST_TIMEOUT,
    }


def get_image_config() -> Dict[str, Any]:
    return {
        "timeout": OPENAI_REQUEST_TIMEOUT,
        "format": IMAGE_FORMAT,
        "quality": IMAGE_QUALITY,
    }
