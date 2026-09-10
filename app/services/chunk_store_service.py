from app.services.chunking import create_chunks
from app.services.embedding_service import generate_embedding
from app.database.repositories.document_repositories import store_documents_bulk
from app.core.logger import logger


def chunk_and_store_document(
    text: str,
    file_name: str,
    document_type: str,
) -> dict:
    """
    Split a document into chunks, generate embeddings,
    and store all chunks in PostgreSQL.
    """

    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    if not file_name or not file_name.strip():
        raise ValueError("File name cannot be empty.")

    if not document_type or not document_type.strip():
        raise ValueError("Document type cannot be empty.")

    # --------------------------------
    # 1. Create chunks
    # --------------------------------

    chunks = create_chunks(text=text)

    if not chunks:
        raise ValueError("No chunks were created.")

    total_chunks = len(chunks)

    # --------------------------------
    # 2. Generate embeddings
    # --------------------------------

    documents = []

    for chunk_index, chunk in enumerate(chunks):

        embedding = generate_embedding(chunk)

        metadata = {
            "file_name": file_name,
            "type": document_type,
            "chunk_index": chunk_index,
            "total_chunks": total_chunks,
        }

        documents.append(
            {
                "text": chunk,
                "embedding": embedding,
                "metadata": metadata,
            }
        )

    # --------------------------------
    # 3. Bulk store in database
    # --------------------------------

    inserted_count = store_documents_bulk(
        documents_list=documents
    )

    logger.debug(
        f"Successfully processed document "
        f"'{file_name}' with {inserted_count} chunks."
    )

    return {
        "success": True,
        "file_name": file_name,
        "type": document_type,
        "number_of_chunks": inserted_count,
    }