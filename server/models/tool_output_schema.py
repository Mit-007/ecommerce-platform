from pydantic import BaseModel
from typing import Optional ,Union

class ToolResponse(BaseModel):
    success: bool
    data: Optional[Union[dict, list,tuple, str]] = None
    error: Optional[str] = None