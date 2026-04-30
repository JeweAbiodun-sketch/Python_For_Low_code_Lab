# Install first if needed:
# pip install pydantic openai pandas pillow requests

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, List
from enum import Enum
import base64
import json
import os
import time
from io import BytesIO
from datetime import datetime

from openai import OpenAI
from PIL import Image
import requests


# =========================
# 1. SETUP
# =========================
api_key = os.environ.get("OPENAI_API_KEY")

if api_key:
    client = OpenAI(api_key=api_key)
else:
    client = None
    print("⚠ Warning: OPENAI_API_KEY not set. Validation demo will work, but OpenAI calls will fail.")


# =========================
# 2. PYDANTIC MODELS
# =========================
class ProductCategory(str, Enum):
    APPAREL = "Apparel"
    ACCESSORIES = "Accessories"
    FOOTWEAR = "Footwear"
    ELECTRONICS = "Electronics"
    HOME = "Home"
    BEAUTY = "Beauty"
    SPORTS = "Sports"
    OTHER = "Other"


class ProductGender(str, Enum):
    MEN = "Men"
    WOMEN = "Women"
    UNISEX = "Unisex"
    KIDS = "Kids"


class ProductInput(BaseModel):
    product_id: str = Field(..., min_length=1, max_length=50)
    product_name: str = Field(..., min_length=3, max_length=200)
    price: float = Field(..., gt=0, le=100000)
    currency: str = Field(default="USD", pattern=r"^[A-Z]{3}$")
    category: ProductCategory
    gender: Optional[ProductGender] = None
    color: Optional[str] = Field(default=None, max_length=50)
    brand: Optional[str] = Field(default=None, max_length=100)
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    tags: Optional[List[str]] = None

    @field_validator("product_name")
    @classmethod
    def clean_product_name(cls, value: str) -> str:
        return " ".join(value.strip().split())

    @field_validator("color")
    @classmethod
    def normalize_color(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().title()

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        cleaned = []
        seen = set()
        for tag in value:
            tag_clean = tag.strip().lower()
            if tag_clean and tag_clean not in seen:
                seen.add(tag_clean)
                cleaned.append(tag_clean)
        return cleaned

    @model_validator(mode="after")
    def check_image_provided(self):
        if not self.image_url and not self.image_base64:
            raise ValueError("Either image_url or image_base64 must be provided")
        return self


class GeneratedListing(BaseModel):
    title: str
    description: str
    features: List[str] = []
    tags: List[str] = []


class APIResponse(BaseModel):
    success: bool
    product_id: str
    generated_listing: Optional[GeneratedListing] = None
    error_message: Optional[str] = None
    processing_time_seconds: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =========================
# 3. VALIDATION FUNCTION
# =========================
def validate_product(json_data: dict):
    """
    Validate incoming JSON product data.
    Returns: (validated_product, errors)
    """
    try:
        product = ProductInput(**json_data)
        return product, None
    except Exception as e:
        errors = []
        if hasattr(e, "errors"):
            for error in e.errors():
                field = ".".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                errors.append(f"{field}: {message}")
        else:
            errors.append(str(e))
        return None, errors


def display_validation_result(product_data: dict, test_name: str):
    print(f"\n--- {test_name} ---")
    product, errors = validate_product(product_data)

    if product:
        print("✓ VALIDATION PASSED")
        print(f"  Product ID: {product.product_id}")
        print(f"  Product Name: {product.product_name}")
        print(f"  Price: {product.price} {product.currency}")
        print(f"  Category: {product.category.value}")
        if product.gender:
            print(f"  Gender: {product.gender.value}")
        if product.color:
            print(f"  Color: {product.color}")
        if product.brand:
            print(f"  Brand: {product.brand}")
        if product.tags:
            print(f"  Tags: {product.tags}")
    else:
        print("✗ VALIDATION FAILED")
        for error in errors:
            print(f"  Error: {error}")


# =========================
# 4. IMAGE PROCESSING
# =========================
def get_image_base64(product: ProductInput) -> str:
    if product.image_base64:
        return product.image_base64

    if product.image_url:
        response = requests.get(product.image_url, timeout=15)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content)).convert("RGB")
        buffer = BytesIO()
        image.save(buffer, format="JPEG")
        return base64.b64encode(buffer.getvalue()).decode("utf-8")

    raise ValueError("No valid image source available")


# =========================
# 5. OPENAI LISTING GENERATION
# =========================
def generate_listing(product: ProductInput) -> GeneratedListing:
    if client is None:
        raise ValueError("OPENAI_API_KEY is not set. Cannot call OpenAI API.")

    image_b64 = get_image_base64(product)

    prompt = f"""
Analyze this product image and create an e-commerce listing.

Product Info:
- Name: {product.product_name}
- Category: {product.category.value}
- Brand: {product.brand or 'N/A'}
- Color: {product.color or 'N/A'}
- Price: {product.price} {product.currency}

Return ONLY valid JSON in this format:
{{
  "title": "Attractive product title",
  "description": "Compelling 80-120 word description",
  "features": ["feature1", "feature2", "feature3"],
  "tags": ["tag1", "tag2", "tag3"]
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a professional e-commerce copywriter. Return only valid JSON."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}
                    }
                ]
            }
        ],
        max_tokens=500,
        temperature=0.4
    )

    content = response.choices[0].message.content.strip()

    if content.startswith("```json"):
        content = content.replace("```json", "", 1).strip()
    if content.startswith("```"):
        content = content.replace("```", "", 1).strip()
    if content.endswith("```"):
        content = content[:-3].strip()

    parsed = json.loads(content)
    return GeneratedListing(**parsed)


# =========================
# 6. END-TO-END PROCESSING
# =========================
def process_product_request(json_data: dict) -> APIResponse:
    start_time = time.time()

    product, errors = validate_product(json_data)

    if errors:
        return APIResponse(
            success=False,
            product_id=json_data.get("product_id", "unknown"),
            error_message="; ".join(errors),
            processing_time_seconds=time.time() - start_time
        )

    try:
        listing = generate_listing(product)
        return APIResponse(
            success=True,
            product_id=product.product_id,
            generated_listing=listing,
            processing_time_seconds=time.time() - start_time
        )
    except Exception as e:
        return APIResponse(
            success=False,
            product_id=product.product_id,
            error_message=str(e),
            processing_time_seconds=time.time() - start_time
        )


# =========================
# 7. VALIDATION DEMO
# =========================
def run_validation_demo():
    print("=" * 60)
    print("PYDANTIC VALIDATION DEMONSTRATION")
    print("=" * 60)

    test_cases = [
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
                "tags": ["casual", "CASUAL", "cotton", "comfort"]
            }
        ),
        (
            "Test 2: Negative Price",
            {
                "product_id": "PROD-002",
                "product_name": "Test Product",
                "price": -10.00,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg"
            }
        ),
        (
            "Test 3: Missing Product Name",
            {
                "product_id": "PROD-003",
                "price": 19.99,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg"
            }
        ),
        (
            "Test 4: Invalid Category",
            {
                "product_id": "PROD-004",
                "product_name": "Test Product",
                "price": 29.99,
                "category": "InvalidCategory",
                "image_url": "https://example.com/image.jpg"
            }
        ),
        (
            "Test 5: No Image Provided",
            {
                "product_id": "PROD-005",
                "product_name": "Product Without Image",
                "price": 49.99,
                "category": "Electronics"
            }
        ),
        (
            "Test 6: Invalid Currency Code",
            {
                "product_id": "PROD-006",
                "product_name": "Test Product",
                "price": 29.99,
                "currency": "dollars",
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg"
            }
        ),
        (
            "Test 7: Product Name Too Short",
            {
                "product_id": "PROD-007",
                "product_name": "AB",
                "price": 29.99,
                "category": "Apparel",
                "image_url": "https://example.com/image.jpg"
            }
        ),
        (
            "Test 8: Price Too High",
            {
                "product_id": "PROD-008",
                "product_name": "Expensive Product",
                "price": 999999.99,
                "category": "Electronics",
                "image_url": "https://example.com/image.jpg"
            }
        )
    ]

    for test_name, data in test_cases:
        display_validation_result(data, test_name)

    print("\n" + "=" * 60)
    print("VALIDATION DEMONSTRATION COMPLETE")
    print("=" * 60)


# =========================
# 8. OPTIONAL END-TO-END DEMO
# =========================
def run_end_to_end_demo():
    print("\n" + "=" * 60)
    print("END-TO-END PROCESSING DEMONSTRATION")
    print("=" * 60)

    test_product = {
        "product_id": "DEMO-001",
        "product_name": "Classic Denim Jacket",
        "price": 89.99,
        "currency": "USD",
        "category": "Apparel",
        "gender": "Unisex",
        "color": "Blue",
        "brand": "DenimCo",
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400",
        "tags": ["denim", "casual", "jacket"]
    }

    result = process_product_request(test_product)

    if result.success:
        print("✓ SUCCESS")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"Title: {result.generated_listing.title}")
        print(f"Description: {result.generated_listing.description}")
        print(f"Features: {result.generated_listing.features}")
        print(f"Tags: {result.generated_listing.tags}")
    else:
        print("✗ FAILED")
        print(f"Error: {result.error_message}")


# =========================
# 9. MAIN
# =========================
if __name__ == "__main__":
    run_validation_demo()

    # Uncomment this if you want to test OpenAI generation too
    # run_end_to_end_demo()