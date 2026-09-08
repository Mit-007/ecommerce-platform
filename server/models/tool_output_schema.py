from pydantic import BaseModel
from typing import Optional ,Any

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None