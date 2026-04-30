import os
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from logger import logger


def load_openai_client() -> Optional[OpenAI]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set. OpenAI calls will be disabled.")
        return None

    try:
        client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized successfully")
        return client
    except Exception as exc:
        logger.exception("loaders.load_openai_client: failed to initialize OpenAI client")
        raise RuntimeError(f"loaders.load_openai_client: failed to initialize OpenAI client: {exc}") from exc


def load_validation_test_cases() -> List[Tuple[str, Dict[str, object]]]:
    return [
        (
            "Test 1: Valid Product",
            {
                "product_id": "PROD-001",
                "product_name": "  Premium Cotton T-Shirt  ",
                "price": 29.99,
                "currency": "USD",
                "category": "Apparel",
                "gender": "Men",
                "color": "navy blue",
                "brand": "StyleCo",
                "image_url": "https://example.com/tshirt.jpg",
                "tags": ["casual", "CASUAL", "cotton", "comfort"],
            },
        ),
        (
            "Test 2: Negative Price",
            {
                "product_id": "PROD-002",
                "product_name": "Test Product",
                "price": -10.00,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg",
            },
        ),
        (
            "Test 3: Missing Product Name",
            {
                "product_id": "PROD-003",
                "price": 19.99,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg",
            },
        ),
        (
            "Test 4: Invalid Category",
            {
                "product_id": "PROD-004",
                "product_name": "Test Product",
                "price": 29.99,
                "category": "InvalidCategory",
                "image_url": "https://example.com/image.jpg",
            },
        ),
        (
            "Test 5: No Image Provided",
            {
                "product_id": "PROD-005",
                "product_name": "Product Without Image",
                "price": 49.99,
                "category": "Electronics",
            },
        ),
        (
            "Test 6: Invalid Currency Code",
            {
                "product_id": "PROD-006",
                "product_name": "Test Product",
                "price": 29.99,
                "currency": "dollars",
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg",
            },
        ),
        (
            "Test 7: Product Name Too Short",
            {
                "product_id": "PROD-007",
                "product_name": "AB",
                "price": 29.99,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg",
            },
        ),
        (
            "Test 8: Price Too High",
            {
                "product_id": "PROD-008",
                "product_name": "Expensive Product",
                "price": 999999.99,
                "category": "Electronics",
                "image_url": "https://example.com/image.jpg",
            },
        ),
    ]


def load_end_to_end_sample_product() -> Dict[str, object]:
    return {
        "product_id": "DEMO-001",
        "product_name": "Classic Denim Jacket",
        "price": 89.99,
        "currency": "USD",
        "category": "Apparel",
        "gender": "Unisex",
        "color": "Blue",
        "brand": "DenimCo",
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400",
        "tags": ["denim", "casual", "jacket"],
    }
