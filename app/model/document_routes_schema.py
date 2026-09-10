from pydantic import BaseModel,Field

class DocumentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
