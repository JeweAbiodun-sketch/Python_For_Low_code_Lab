import time
from typing import Any, Optional, Tuple

from api_helpers import build_chat_messages, build_product_prompt, call_openai_chat_api, parse_json_response
from config import get_openai_config
from image_helpers import get_image_base64
from logger import logger
from models import APIResponse, GeneratedListing
from validators import validate_product


def execute_with_timing(func: Any, *args: Any, **kwargs: Any) -> Tuple[float, Any]:
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start_time
    return elapsed, result


def generate_product_listing(product: Any, client: Optional[Any]) -> GeneratedListing:
    logger.debug("processor.generate_product_listing: starting generation for product %s", product.product_id)
    try:
        image_b64 = get_image_base64(product)
        prompt = build_product_prompt(product)
        messages = build_chat_messages(prompt, image_b64)
        config = get_openai_config()
        raw_response = call_openai_chat_api(client, messages, config)
        parsed = parse_json_response(raw_response)
        logger.info("processor.generate_product_listing: listing generated successfully for product %s", product.product_id)
        return GeneratedListing(**parsed)
    except Exception as exc:
        logger.exception("processor.generate_product_listing: failed for product %s", product.product_id)
        raise RuntimeError(f"processor.generate_product_listing: {exc}") from exc


def process_product_request(json_data: dict, client: Optional[Any]) -> APIResponse:
    start_time = time.time()
    product, errors = validate_product(json_data)

    if errors:
        error_text = "; ".join(errors)
        logger.warning(
            "processor.process_product_request: validation failed for product %s: %s",
            json_data.get("product_id", "unknown"),
            error_text,
        )
        return APIResponse(
            success=False,
            product_id=json_data.get("product_id", "unknown"),
            error_message=f"processor.process_product_request: validation failed: {error_text}",
            processing_time_seconds=time.time() - start_time,
        )

    try:
        listing = generate_product_listing(product, client)
        return APIResponse(
            success=True,
            product_id=product.product_id,
            generated_listing=listing,
            processing_time_seconds=time.time() - start_time,
        )
    except Exception as exc:
        logger.error(
            "processor.process_product_request: generation failed for product %s: %s",
            product.product_id,
            exc,
        )
        return APIResponse(
            success=False,
            product_id=product.product_id,
            error_message=f"processor.process_product_request: {exc}",
            processing_time_seconds=time.time() - start_time,
        )
