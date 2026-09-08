from pydantic import BaseModel, Field, validator
from uuid import UUID

class GetOrderRequest(BaseModel):
    order_id: str = Field(..., description="The order ID")

class CreateSupportTicket(BaseModel):
    order_id: str = Field(..., description="The order ID")
    summary : str = Field(...,description="give summary of problem related to order")
    conversation_id : str = Field(...,description="providea a converstion id ")

class GetSupportTicket(BaseModel):
    support_ticket_id: str = Field(..., description="The order ID")