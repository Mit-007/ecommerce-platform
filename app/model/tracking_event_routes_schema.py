from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class TrackingStatus(str, Enum):
    ORDER_PLACED = "order_placed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    EXCEPTION = "exception"


class CreateTrackingEvent(BaseModel):
    status: TrackingStatus
    location: str | None = Field(default=None,max_length=255,)