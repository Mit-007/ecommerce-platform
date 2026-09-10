from fastapi import APIRouter, HTTPException
from app.model.document_routes_schema import DocumentRequest
from app.services.chunk_store_service import chunk_and_store_document
from app.core.logger import logger

router = APIRouter(prefix="/documents",tags=["Documents"],)

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

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except ValueError as e:
        logger.error(f"Invalid document request: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while uploading document: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )