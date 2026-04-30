import base64
from io import BytesIO
from typing import Dict

import requests
from PIL import Image

from config import get_image_config
from logger import logger
from models import ProductInput


def fetch_image_from_url(url: str, timeout: int) -> bytes:
    logger.debug("image_helpers.fetch_image_from_url: fetching image from %s", url)
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as exc:
        logger.exception("image_helpers.fetch_image_from_url: failed to download image from %s", url)
        raise RuntimeError(
            f"image_helpers.fetch_image_from_url: failed to download image from {url}: {exc}"
        ) from exc


def convert_bytes_to_base64_jpeg(image_bytes: bytes, format: str = "JPEG", quality: int = 95) -> str:
    logger.debug("image_helpers.convert_bytes_to_base64_jpeg: converting image bytes to base64 JPEG")
    try:
        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format=format, quality=quality)
        return base64.b64encode(buffer.getvalue()).decode("utf-8")
    except Exception as exc:
        logger.exception("image_helpers.convert_bytes_to_base64_jpeg: failed to convert image bytes")
        raise RuntimeError(
            f"image_helpers.convert_bytes_to_base64_jpeg: failed to convert image bytes to base64 JPEG: {exc}"
        ) from exc


def get_image_base64(product: ProductInput) -> str:
    logger.debug("image_helpers.get_image_base64: retrieving image for product %s", product.product_id)
    if product.image_base64:
        return product.image_base64

    if product.image_url:
        config = get_image_config()
        image_bytes = fetch_image_from_url(product.image_url, timeout=config["timeout"])
        return convert_bytes_to_base64_jpeg(
            image_bytes,
            format=config["format"],
            quality=config["quality"],
        )

    raise ValueError("image_helpers.get_image_base64: no valid image source available")


def validate_image_source(product: ProductInput) -> bool:
    return bool(product.image_url or product.image_base64)
