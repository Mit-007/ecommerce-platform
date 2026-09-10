from pydantic import BaseModel
from uuid import UUID

class AgentRequest(BaseModel):
    message: str
    conversation_id: UUID | None = None
    customer_id : UUID | None = None
