import json
from typing import Any, Dict, List, Optional

from config import PROMPT_TEMPLATE, SYSTEM_PROMPT, get_openai_config
from logger import logger
from models import GeneratedListing, ProductInput


def build_product_prompt(product: ProductInput) -> str:
    logger.debug("api_helpers.build_product_prompt: building prompt for product %s", product.product_id)
    try:
        return PROMPT_TEMPLATE.format(
            name=product.product_name,
            category=product.category.value,
            brand=product.brand or "N/A",
            color=product.color or "N/A",
            price=product.price,
            currency=product.currency,
        )
    except Exception as exc:
        logger.exception("api_helpers.build_product_prompt: failed to build prompt for product %s", product.product_id)
        raise RuntimeError(
            f"api_helpers.build_product_prompt: failed to build prompt for product {product.product_id}: {exc}"
        ) from exc


def build_chat_messages(prompt: str, image_b64: str) -> List[Dict[str, Any]]:
    logger.debug("api_helpers.build_chat_messages: building chat payload")
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"},
                },
            ],
        },
    ]


def call_openai_chat_api(client: Any, messages: List[Dict[str, Any]], config: Dict[str, Any]) -> str:
    if client is None:
        logger.error("api_helpers.call_openai_chat_api: OpenAI client is not initialized")
        raise RuntimeError("api_helpers.call_openai_chat_api: OpenAI client is not initialized")

    try:
        logger.info("api_helpers.call_openai_chat_api: sending OpenAI request")
        response = client.chat.completions.create(
            model=config["model"],
            messages=messages,
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
        )
        return response.choices[0].message.content
    except Exception as exc:
        logger.exception("api_helpers.call_openai_chat_api: OpenAI API request failed")
        raise RuntimeError(
            f"api_helpers.call_openai_chat_api: OpenAI API request failed: {exc}"
        ) from exc


def clean_markdown_code_blocks(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


def parse_json_response(text: str) -> dict:
    cleaned = clean_markdown_code_blocks(text)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.exception("api_helpers.parse_json_response: failed to parse JSON response")
        raise RuntimeError(
            f"api_helpers.parse_json_response: failed to parse JSON response: {exc}"
        ) from exc


def validate_listing_response(data: dict) -> tuple[bool, Optional[str]]:
    try:
        GeneratedListing(**data)
        return True, None
    except Exception as exc:
        return False, f"api_helpers.validate_listing_response: invalid listing response: {exc}"
