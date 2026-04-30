# API Calling with JSON

This project validates product data with Pydantic, generates AI-powered e-commerce product listings using OpenAI, and supports a FastAPI wrapper for API access.

## Project Structure

- `product_generator_refactored.py` — original validation and generation demo script
- `models.py` — Pydantic models for product input, generated listing, and API response
- `config.py` — constants and OpenAI configuration
- `loaders.py` — environment and sample/test data loaders
- `validators.py` — validation helpers and error extraction
- `image_helpers.py` — image download and base64 conversion helpers
- `api_helpers.py` — OpenAI prompt, message, API call, and response parsing
- `processor.py` — orchestration layer for full request processing
- `output.py` — display and formatting helpers
- `api_wrapper.py` — FastAPI wrapper for validation and generation endpoints
- `REFACTORING_PLAN.md` — refactor plan and helper structure

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
pip install pydantic openai pillow requests fastapi uvicorn
```

3. Set your OpenAI API key:

```bash
setx OPENAI_API_KEY "your_api_key"
```

4. (Optional) Configure log verbosity:

```bash
setx LOG_LEVEL "DEBUG"
```

By default, log output is written to the console using the shared `logger.py` configuration.

## Running the CLI Demo

Run the main script for validation and optional end-to-end demo:

```bash
python product_generator_refactored.py
```

## API Wrapper

The FastAPI wrapper is provided in `api_wrapper.py`.

### Start the API server

```bash
uvicorn api_wrapper:app --reload
```

### Available endpoints

- `GET /health`
  - Returns `{ "status": "healthy" }`

- `POST /api/v1/product/validate`
  - Validates raw product JSON.
  - Returns validation success or field-level errors.

- `POST /api/v1/product/generate`
  - Accepts validated `ProductInput` data.
  - Returns generated product listing and metadata.

- `POST /api/v1/product/batch`
  - Accepts a list of products.
  - Returns individual results for each item.

### Example request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/product/generate" \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## Error Handling

The API wrapper includes explicit error location metadata for validation and generation failures, such as:

- `validators.validate_product`
- `processor.process_product_request`

This helps identify where a request failed in the processing flow.
