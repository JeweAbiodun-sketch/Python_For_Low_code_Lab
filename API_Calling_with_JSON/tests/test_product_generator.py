import base64
from io import BytesIO
from typing import Any, Dict

import pytest
from fastapi.testclient import TestClient
from PIL import Image

import api_wrapper
import api_helpers
import processor
from models import APIResponse, GeneratedListing, ProductListingResponse
from validators import validate_product
from processor import process_product_request


def build_test_image_base64() -> str:
    image = Image.new("RGB", (64, 64), color="blue")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def valid_product_payload() -> Dict[str, Any]:
    return {
        "product_id": "TEST-100",
        "product_name": "Premium Running Sneakers",
        "price": 120.0,
        "currency": "USD",
        "category": "Footwear",
        "gender": "Unisex",
        "color": "Black",
        "brand": "RunPro",
        "image_base64": build_test_image_base64(),
        "tags": ["running", "fitness", "comfort"],
    }


def invalid_product_payload() -> Dict[str, Any]:
    return {
        "product_id": "TEST-101",
        "product_name": "  ",
        "price": -5.0,
        "currency": "usd",
        "category": "Gadgets",
    }


def test_validate_product_success():
    payload = valid_product_payload()
    product, errors = validate_product(payload)

    assert product is not None
    assert errors is None
    assert product.product_id == "TEST-100"
    assert product.currency == "USD"
    assert product.category.value == "Footwear"
    assert product.image_base64 is not None


def test_validate_product_failure():
    payload = invalid_product_payload()
    product, errors = validate_product(payload)

    assert product is None
    assert errors is not None
    assert any("product_name" in err for err in errors)
    assert any("price" in err for err in errors)
    assert any("currency" in err for err in errors)
    assert any("category" in err for err in errors)


def test_process_product_request_success(monkeypatch):
    payload = valid_product_payload()
    fake_response = '{"title":"Demo Title","description":"Demo description.","features":["feature1","feature2"],"tags":["demo"]}'

    monkeypatch.setattr(processor, "call_openai_chat_api", lambda *_args, **_kwargs: fake_response)

    result = process_product_request(payload, object())

    assert result.success is True
    assert result.error_message is None
    assert result.generated_listing is not None
    assert result.generated_listing.title == "Demo Title"
    assert result.generated_listing.features == ["feature1", "feature2"]


def test_process_product_request_validation_failure():
    payload = invalid_product_payload()

    result = process_product_request(payload, object())

    assert result.success is False
    assert result.generated_listing is None
    assert "product_name" in result.error_message
    assert "price" in result.error_message


def test_process_product_request_image_failure(monkeypatch):
    payload = valid_product_payload()

    def raise_image_error(*args, **kwargs):
        raise RuntimeError("failed to download image")

    monkeypatch.setattr(processor, "get_image_base64", raise_image_error)

    result = process_product_request(payload, object())

    assert result.success is False
    assert result.generated_listing is None
    assert "failed to download image" in result.error_message


def test_api_validate_endpoint():
    client = TestClient(api_wrapper.app)

    valid_response = client.post("/api/v1/product/validate", json=valid_product_payload())
    assert valid_response.status_code == 200
    assert valid_response.json()["success"] is True
    assert valid_response.json()["product_id"] == "TEST-100"

    invalid_response = client.post("/api/v1/product/validate", json=invalid_product_payload())
    assert invalid_response.status_code == 400
    assert invalid_response.json()["success"] is False
    assert invalid_response.json()["error_location"] == "validators.validate_product"


def test_api_generate_endpoint_success(monkeypatch):
    payload = valid_product_payload()
    fake_listing = ProductListingResponse(
        success=True,
        product_id=payload["product_id"],
        generated_listing=GeneratedListing(
            title="API Demo Title",
            description="API demo description.",
            features=["api-feature1"],
            tags=["api-demo"],
        ),
        processing_time_seconds=0.01,
    )

    monkeypatch.setattr(api_wrapper, "client", object())
    monkeypatch.setattr(api_wrapper, "process_product_request", lambda *_args, **_kwargs: fake_listing)

    client = TestClient(api_wrapper.app)
    response = client.post("/api/v1/product/generate", json=payload)

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["generated_listing"]["title"] == "API Demo Title"


def test_api_generate_endpoint_failure(monkeypatch):
    payload = valid_product_payload()
    fake_failure = APIResponse(
        success=False,
        product_id=payload["product_id"],
        error_message="processor failure",
        processing_time_seconds=0.02,
    )

    monkeypatch.setattr(api_wrapper, "client", object())
    monkeypatch.setattr(api_wrapper, "process_product_request", lambda *_args, **_kwargs: fake_failure)

    client = TestClient(api_wrapper.app)
    response = client.post("/api/v1/product/generate", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"]["location"] == "processor.process_product_request"
    assert "processor failure" in response.json()["detail"]["message"]
