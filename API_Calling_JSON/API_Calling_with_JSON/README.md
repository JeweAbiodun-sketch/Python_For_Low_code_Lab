# API Calling with JSON

This project validates product data with Pydantic, generates AI-powered e-commerce product listings using OpenAI, and supports a FastAPI wrapper for API access.

## Project Structure

The repository contains the following Jupyter notebooks from the `API_Calling_JSON` workflow:

- `product_generator_refactored.ipynb` — main validation and generation demo notebook with Pydantic models and OpenAI integration
- `api_json_generator_refactored.ipynb` — alternative refactored API JSON generator notebook
- `API_JSON.ipynb` — API JSON handling notebook
- `models.ipynb` — Pydantic models for product input, generated listing, and API response
- `config.ipynb` — constants and OpenAI configuration
- `api_helpers.ipynb` — OpenAI prompt, message, API call, and response parsing
- `logger.ipynb` — logging configuration
- `VALIDATION_TEST_RESULTS.md` — documented validation test results and behavior comparison
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

By default, log output is written to the console using the shared `logger.ipynb` configuration.

## Running the Demo

Open `product_generator_refactored.ipynb` in Jupyter and run the cells to see:
- Pydantic validation demonstrations
- End-to-end product listing generation (requires OpenAI API key)

## API Wrapper

The `api_wrapper.ipynb` notebook contains a FastAPI application for serving the product generation functionality as a web API.

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
