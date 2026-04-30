# Refactoring Plan for API JSON Generator

## Brief Analysis

### Monolithic Function Example

- `generate_listing(product: ProductInput)` is currently too large.
- It handles:
  - image retrieval and conversion to base64
  - OpenAI prompt construction
  - API request building and execution
  - JSON response normalization and parsing
  - response validation via Pydantic

This is a classic case of mixed concerns and should be split into focused helpers.

## Refactor Plan

### Proposed module structure

- `config.py` — constants and configuration
- `loaders.py` — environment and test data loading
- `validators.py` — validation and error extraction
- `image_helpers.py` — URL download, conversion, and base64 encoding
- `api_helpers.py` — prompt building, message assembly, API call, and JSON parsing
- `processor.py` — orchestration and request flow
- `output.py` — text formatting and display

### Proposed helper functions

#### Loading function
- `load_environment()`
- `load_validation_test_cases()`
- `load_end_to_end_sample_product()`

#### Validation function
- `validate_product(json_data: dict) -> tuple[Optional[ProductInput], Optional[List[str]]]`
- `extract_pydantic_errors(exc: Exception) -> List[str]`

#### Image helper functions
- `fetch_image_from_url(url: str, timeout: int) -> bytes`
- `convert_bytes_to_base64_jpeg(image_bytes: bytes, quality: int = 95) -> str`
- `get_image_base64(product: ProductInput) -> str`
- `validate_image_source(product: ProductInput) -> bool`

#### API helper functions
- `build_product_prompt(product: ProductInput) -> str`
- `build_chat_messages(prompt: str, image_b64: str) -> List[dict]`
- `call_openai_chat_api(client: OpenAI, messages: List[dict], config: dict) -> str`
- `clean_markdown_code_blocks(text: str) -> str`
- `parse_json_response(text: str) -> dict`
- `validate_listing_response(data: dict) -> tuple[bool, Optional[str]]`

#### Processing/orchestration functions
- `generate_product_listing(product: ProductInput, client: OpenAI) -> GeneratedListing`
- `process_product_request(json_data: dict, client: Optional[OpenAI]) -> APIResponse`
- `execute_with_timing(func, *args, **kwargs) -> tuple[float, Any]`

#### Saving/output functions
- `print_section_header(title: str, width: int = 60) -> None`
- `print_section_footer(width: int = 60) -> None`
- `format_product_details(product: ProductInput) -> str`
- `format_validation_errors(errors: List[str]) -> str`
- `display_validation_test(test_name: str, product_data: dict) -> None`
- `display_end_to_end_result(result: APIResponse) -> None`

## Example split for `generate_listing`

Current responsibilities in one function:
- image handling
- prompt text generation
- OpenAI request execution
- API response cleanup
- JSON parsing

Refactor into these helpers:
- `get_image_base64(product)`
- `build_product_prompt(product)`
- `build_chat_messages(prompt, image_b64)`
- `call_openai_chat_api(client, messages, config)`
- `parse_json_response(content)`

## Result

This refactor keeps each function focused on a single responsibility and makes the code easier to test and maintain.
