from typing import List
from server.database.connection import get_db_connection, release_db_connection
from server.core.constant import OUTPUT_DIMENSIONALITY
from server.core.logger import logger

def search_documents_by_vector(
    embedding: List[float],
    top_n,
) -> List[dict]:
    """
    Search documents using pgvector cosine similarity.
    
    Retrieves the top N most relevant document chunks from PostgreSQL
    by calculating cosine similarity between the query embedding and
    stored document embeddings.
    
    Args:
        embedding: Query embedding vector (list of floats)
        top_n: Number of top results to return (1-20, default 5)
        
    Returns:
        List of dictionaries containing: document_id, original_text, metadata, created_at, similarity_score
        
    Raises:
        ValueError: If embedding is invalid or top_n is out of range
        Exception: If database operation fails
    """    
    if not embedding or not isinstance(embedding, (list, tuple)):
        raise ValueError("Embedding must be a non-empty list or tuple of floats")
    
    if len(embedding) != OUTPUT_DIMENSIONALITY:
        raise ValueError(f"Embedding must have exactly {OUTPUT_DIMENSIONALITY} dimensions")
    
    conn = None
    cur = None
    
    try:
        conn, cur = get_db_connection()
        
        # Execute vector similarity search using cosine distance operator (<=>)
        cur.execute(
            """
            SELECT
                document_id,
                original_text,
                metadata,
                created_at,
                1 - (embedding_vector <=> %s::vector) AS similarity_score
            FROM document
            WHERE embedding_vector IS NOT NULL
            ORDER BY embedding_vector <=> %s::vector
            LIMIT %s
            """,
            (
                embedding,
                embedding,
                top_n,
            ),
        )
        
        rows = cur.fetchall()
        
        if not rows:
            logger.info("No documents found matching the query embedding")
            return []
        
        results = []
        for row in rows:
            results.append(row[1] if row[1] else "")
            logger.info(30*"-")
            logger.info(row[2])
        
        logger.info(f"Successfully retrieved {len(results)} documents from vector search")
        return results
        
    except ValueError as e:
        raise
        
    except Exception as e:
        raise Exception(f"Vector search operation failed: {str(e)}")
        
    finally:
        if conn:
            release_db_connection(conn, cur)
