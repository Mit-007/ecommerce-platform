from pydantic import BaseModel, Field
from typing import Optional


class CreateProduct(BaseModel):
    category: str = Field(..., min_length=1, max_length=255, description="Product category")
    sub_category: Optional[str] = Field(None, max_length=255, description="Product subcategory")
    name: str = Field(..., min_length=1, max_length=255, description="Product name")
    image_url: Optional[str] = Field(None, description="Product image URL")
    rating: float = Field(0.0, ge=0.0, le=5.0, description="Product rating (0-5)")
    total_rating: int = Field(0, ge=0, description="Total number of ratings")
    price: float = Field(..., ge=0.0, description="Product price")


class UpdateProduct(BaseModel):
    category: Optional[str] = Field(None, min_length=1, max_length=255, description="Product category")
    sub_category: Optional[str] = Field(None, max_length=255, description="Product subcategory")
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Product name")
    image_url: Optional[str] = Field(None, description="Product image URL")
    rating: Optional[float] = Field(None, ge=0.0, le=5.0, description="Product rating (0-5)")
    total_rating: Optional[int] = Field(None, ge=0, description="Total number of ratings")
    price: Optional[float] = Field(None, ge=0.0, description="Product price")
