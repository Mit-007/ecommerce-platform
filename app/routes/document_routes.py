from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.chunk_store_service import (
    chunk_and_store_document,
)
from app.core.logger import logger


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


class DocumentRequest(BaseModel):
    text: str = Field(..., min_length=1)
    file_name: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)


@router.post("/upload")
def upload_document(request: DocumentRequest):
    """
    Chunk the document, generate embeddings,
    and store all chunks in PostgreSQL.
    """
    try:
        result = chunk_and_store_document(
            text=request.text,
            file_name=request.file_name,
            document_type=request.type,
        )

        return result

    except ValueError as e:
        logger.warning(f"Invalid document request: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        logger.exception(
            f"Failed to upload document: {e}"
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to process document.",
        )