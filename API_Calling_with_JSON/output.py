from typing import List

from models import APIResponse, ProductInput
from validators import validate_product


def print_section_header(title: str, width: int = 60) -> None:
    print("=" * width)
    print(title)
    print("=" * width)


def print_section_footer(width: int = 60) -> None:
    print("\n" + "=" * width)


def format_product_details(product: ProductInput) -> str:
    lines = [
        f"Product ID: {product.product_id}",
        f"Product Name: {product.product_name}",
        f"Price: {product.price} {product.currency}",
        f"Category: {product.category.value}",
    ]
    if product.gender:
        lines.append(f"Gender: {product.gender.value}")
    if product.color:
        lines.append(f"Color: {product.color}")
    if product.brand:
        lines.append(f"Brand: {product.brand}")
    if product.tags:
        lines.append(f"Tags: {product.tags}")
    return "\n".join(lines)


def format_validation_errors(errors: List[str]) -> str:
    return "\n".join(f"Error: {error}" for error in errors)


def display_validation_test(test_name: str, product_data: dict) -> None:
    print(f"\n--- {test_name} ---")
    product, errors = validate_product(product_data)

    if product:
        print("✓ VALIDATION PASSED")
        print(format_product_details(product))
    else:
        print("✗ VALIDATION FAILED")
        print(format_validation_errors(errors or ["Unknown validation error"]))


def display_end_to_end_result(result: APIResponse) -> None:
    if result.success and result.generated_listing:
        print("✓ SUCCESS")
        print(f"Processing time: {result.processing_time_seconds:.2f}s")
        print(f"Title: {result.generated_listing.title}")
        print(f"Description: {result.generated_listing.description}")
        print(f"Features: {result.generated_listing.features}")
        print(f"Tags: {result.generated_listing.tags}")
    else:
        print("✗ FAILED")
        print(f"Error: {result.error_message}")
