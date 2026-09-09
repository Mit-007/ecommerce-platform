from typing import List
from server.database.connection import get_db_connection,release_db_connection
from server.core.logger import logger

def search_documents_by_vector(
    embedding: List[float],
    top_n: int = 5,
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
    logger.info(f"Searching documents with top_n={top_n}")
    
    if not embedding or not isinstance(embedding, (list, tuple)):
        logger.error("Invalid embedding provided")
        raise ValueError("Embedding must be a non-empty list or tuple of floats")
    
    if len(embedding) != 3072:
        logger.error(f"Invalid embedding dimension: expected 3072, got {len(embedding)}")
        raise ValueError("Embedding must have exactly 3072 dimensions")
    
    if top_n <= 0 or top_n > 20:
        logger.error(f"Invalid top_n value: {top_n}")
        raise ValueError("top_n must be between 1 and 20")
    
    conn = None
    cur = None
    
    try:
        conn, cur = get_db_connection()
        
        if not conn or not cur:
            logger.error("Failed to establish database connection")
            raise Exception("Database connection failed")
        
        # Convert embedding list to PostgreSQL vector format
        embedding_string = "[" + ",".join(str(value) for value in embedding) + "]"
        
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
                embedding_string,
                embedding_string,
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
        
        logger.info(f"Successfully retrieved {len(results)} documents from vector search")
        return results
        
    except ValueError as e:
        logger.warning(f"Validation error in search_documents_by_vector: {str(e)}")
        raise
        
    except Exception as e:
        logger.error(f"Database error in search_documents_by_vector: {str(e)}", exc_info=True)
        raise Exception(f"Vector search operation failed: {str(e)}")
        
    finally:
        if conn and cur:
            try:
                release_db_connection(conn, cur)
            except Exception as e:
                logger.warning(f"Error releasing database connection: {str(e)}")