from datetime import date
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field


# --- create new order
class OrderStatus(str, Enum): 
    PENDING = "pending" 
    PROCESSING = "processing" 
    SHIPPED = "shipped" 
    DELIVERED = "delivered" 
    CANCELLED = "cancelled" 
    RETURNED = "returned"


class OrderItem(BaseModel):
    name: str = Field(...,min_length=1,max_length=255,)
    quantity: int = Field(...,gt=0,)

class CreateOrder(BaseModel):
    customer_id: UUID
    invoice_id: UUID
    status: OrderStatus = OrderStatus.PENDING
    estimated_delivery_date: date | None = None
    returnable: bool = False
    product_list: list[OrderItem] = Field(...,min_length=1,)


# --- all services regarding order_id
# get/{order_id}
# put/{order_id}
# delete/{order_id}
# get/{order_id}/items
# get/{order_id}/tracking


class OrderRequest(BaseModel):
    order_id : UUID
