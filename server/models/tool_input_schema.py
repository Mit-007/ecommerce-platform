from pydantic import BaseModel, Field
from server.core.constant import DEFAULT_TOP_N, MAXIMUM_RETRIEVAL_CHUNK

class GetOrderRequest(BaseModel):
    order_id: str = Field(..., description="The order ID")

class CreateSupportTicket(BaseModel):
    order_id: str = Field(..., description="The order ID")
    summary : str = Field(...,description="give summary of problem related to order")
    conversation_id : str = Field(...,description="provide a conversation id ")

class GetSupportTicket(BaseModel):
    support_ticket_id: str = Field(..., description="The order ID")

class searchQuery(BaseModel):
    query: str = Field(...,description="give query for performe a similarity search")
    top_n: int = Field(DEFAULT_TOP_N,gt=0,le=MAXIMUM_RETRIEVAL_CHUNK, description=(f"Number of documents to retrieve.Must be between 1 and {MAXIMUM_RETRIEVAL_CHUNK}."))