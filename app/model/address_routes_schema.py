from pydantic import BaseModel, Field
from typing import Optional


class CreateAddress(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=100, description="Full name of recipient")
    phone: str = Field(..., min_length=1, max_length=15, description="Contact phone number")
    address_line1: str = Field(..., min_length=1, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2 (optional)")
    city: str = Field(..., min_length=1, max_length=100, description="City")
    state: str = Field(..., min_length=1, max_length=100, description="State")
    postal_code: str = Field(..., min_length=1, max_length=10, description="Postal / ZIP code")
    country: str = Field("India", min_length=1, max_length=100, description="Country")
    is_default: bool = Field(False, description="Whether this is the default address")


class UpdateAddress(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Full name of recipient")
    phone: Optional[str] = Field(None, min_length=1, max_length=15, description="Contact phone number")
    address_line1: Optional[str] = Field(None, min_length=1, max_length=255, description="Address line 1")
    address_line2: Optional[str] = Field(None, max_length=255, description="Address line 2")
    city: Optional[str] = Field(None, min_length=1, max_length=100, description="City")
    state: Optional[str] = Field(None, min_length=1, max_length=100, description="State")
    postal_code: Optional[str] = Field(None, min_length=1, max_length=10, description="Postal / ZIP code")
    country: Optional[str] = Field(None, min_length=1, max_length=100, description="Country")
    is_default: Optional[bool] = Field(None, description="Whether this is the default address")
