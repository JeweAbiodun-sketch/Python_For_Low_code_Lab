from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


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
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ProductListingResponse(BaseModel):
    success: bool
    product_id: str
    generated_listing: GeneratedListing
    processing_time_seconds: float
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
