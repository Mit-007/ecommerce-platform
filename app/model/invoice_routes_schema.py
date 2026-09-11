from enum import Enum
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class CreateInvoice(BaseModel):
    customer_id: UUID
    invoice_number: str = Field(...,min_length=1,max_length=255,)
    status: InvoiceStatus = InvoiceStatus.DRAFT

class UpdateInvoiceStatus(BaseModel):
    status: InvoiceStatus
