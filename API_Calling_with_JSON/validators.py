from typing import Any, List, Optional, Tuple

from logger import logger
from models import ProductInput


def extract_pydantic_errors(exc: Exception) -> List[str]:
    errors: List[str] = []
    if hasattr(exc, "errors"):
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_message = f"validators.validate_product: {field}: {message}"
            logger.debug(error_message)
            errors.append(error_message)
    else:
        error_message = f"validators.validate_product: {str(exc)}"
        logger.debug(error_message)
        errors.append(error_message)
    return errors


def validate_product(json_data: dict) -> Tuple[Optional[ProductInput], Optional[List[str]]]:
    try:
        product = ProductInput(**json_data)
        return product, None
    except Exception as exc:
        return None, extract_pydantic_errors(exc)
