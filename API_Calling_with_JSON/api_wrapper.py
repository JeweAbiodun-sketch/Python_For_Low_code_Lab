from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any

from loaders import load_openai_client
from logger import logger
from models import ProductInput, ProductListingResponse
from processor import process_product_request
from validators import validate_product

app = FastAPI(
    title="Product Listing Generator API",
    description="API wrapper for product validation and listing generation using OpenAI.",
    version="1.0.0",
)

client = load_openai_client()
logger.info("api_wrapper: API wrapper initialized. OpenAI client available=%s", client is not None)


@app.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy"}


@app.post("/api/v1/product/validate")
def validate_product_endpoint(product_data: Dict[str, Any]) -> Any:
    logger.debug("api_wrapper.validate_product_endpoint: received product_data with id=%s", product_data.get("product_id"))
    product, errors = validate_product(product_data)
    if errors:
        logger.warning(
            "api_wrapper.validate_product_endpoint: validation failed for product %s: %s",
            product_data.get("product_id"),
            errors,
        )
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error_location": "validators.validate_product",
                "errors": errors,
            },
        )

    return {
        "success": True,
        "product_id": product.product_id,
        "validated_data": product.model_dump(),
    }


@app.post("/api/v1/product/generate", response_model=ProductListingResponse)
def generate_product_listing_endpoint(product: ProductInput) -> ProductListingResponse:
    logger.debug(
        "api_wrapper.generate_product_listing_endpoint: received generation request for product %s",
        product.product_id,
    )
    if client is None:
        logger.error("api_wrapper.generate_product_listing_endpoint: missing OpenAI client")
        raise HTTPException(
            status_code=500,
            detail="api_wrapper: OPENAI_API_KEY is not configured, so generation cannot proceed.",
        )

    result = process_product_request(product.model_dump(), client)
    if not result.success:
        logger.warning(
            "api_wrapper.generate_product_listing_endpoint: generation error for product %s: %s",
            product.product_id,
            result.error_message,
        )
        raise HTTPException(
            status_code=400,
            detail={
                "location": "processor.process_product_request",
                "message": result.error_message,
            },
        )
    logger.info("api_wrapper.generate_product_listing_endpoint: generation success for product %s", product.product_id)
    return result


@app.post("/api/v1/product/batch")
def batch_generate_endpoint(products: List[Dict[str, Any]]) -> Any:
    if client is None:
        logger.error("api_wrapper.batch_generate_endpoint: missing OpenAI client")
        raise HTTPException(
            status_code=500,
            detail="api_wrapper: OPENAI_API_KEY is not configured, so batch generation cannot proceed.",
        )

    responses = []
    for index, product_data in enumerate(products, start=1):
        product, errors = validate_product(product_data)
        if errors:
            logger.warning(
                "api_wrapper.batch_generate_endpoint: validation failed for batch item %s: %s",
                product_data.get("product_id", f"item_{index}"),
                errors,
            )
            responses.append(
                {
                    "success": False,
                    "product_id": product_data.get("product_id", f"item_{index}"),
                    "error_location": "validators.validate_product",
                    "errors": errors,
                }
            )
            continue

        result = process_product_request(product.model_dump(), client)
        if not result.success:
            logger.warning(
                "api_wrapper.batch_generate_endpoint: generation failed for product %s: %s",
                result.product_id,
                result.error_message,
            )
            responses.append(
                {
                    "success": False,
                    "product_id": result.product_id,
                    "error_location": "processor.process_product_request",
                    "message": result.error_message,
                }
            )
        else:
            logger.info("api_wrapper.batch_generate_endpoint: generated product %s successfully", result.product_id)
            responses.append(result.model_dump())

    return {"results": responses}
