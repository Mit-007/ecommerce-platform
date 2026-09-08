from fastmcp import FastMCP
from server.database.connection import (
    get_db_connection,
    release_db_connection,
)
from server.core.logger import logger
from server.services.embedding_service import generate_embedding
from server.models.tool_output_schema import ToolResponse

def register_search_tools(mcp: FastMCP):
    @mcp.tool()
    def search_query(
        query: str,
        top_n: int = 5,
    ) -> dict:
        """
        Retrieve the top N most relevant document chunks
        from PostgreSQL using pgvector cosine similarity.
        """
        logger.info("Tool_call : search_query")

        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
 
        if top_n <= 0:
            raise ValueError("top_n must be greater than 0.")
 
        top_n = min(top_n, 20)
 
        conn = None
        cur = None
 
        try:
            
            # ================================
            # 1. GENERATE QUERY EMBEDDING
            # ================================
 
            query_embedding = generate_embedding(query)

            embedding_string = "[" + ",".join(
                str(value) for value in query_embedding
            ) + "]"
 
            # ================================
            # 2. VECTOR SIMILARITY SEARCH
            # ================================
 
            conn, cur = get_db_connection()
 
            cur.execute(
                """
                SELECT
                    document_id,
                    original_text,
                    metadata,
                    created_at,
                    1-(embedding_vector <=> %s::vector) AS similarity
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
            
            # ================================
            # 3. CONVERT RESULTS
            # ================================
 
            text_data = []
 
            for row in rows:
                logger.info("---------------------------------------------------------------------------------")
                logger.info("chunk details")
                logger.info("--------------------------------")
                logger.info(row)
                text_data.append(row[1])
 
            logger.info(f"Retrieved {len(text_data)} chunks for query")
 
            # ================================
            # 4. RETURN RESULTS
            # ================================

            return ToolResponse(
                success=True,
                data=text_data,
                error=None
            )
 
        except Exception as e:
            logger.exception(f"Failed to retrieve document chunks: {e}")
            return ToolResponse(
                success=False,
                data=[],
                error=str(e)
            )
 
        finally:
            if conn:
                release_db_connection(conn, cur)