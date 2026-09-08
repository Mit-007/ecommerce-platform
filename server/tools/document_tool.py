import json
from fastmcp import FastMCP
from server.database.connection import (
    get_db_connection,
    release_db_connection,
)
from server.services.chunking import create_chunks
from server.services.embedding_service import generate_embedding
from server.core.logger import logger


def register_document_tools(mcp: FastMCP):

    @mcp.tool()
    def chunk_and_store_document(
        text: str,
        file_name: str,
        type: str,
    ) -> dict:
        """
        Split text into chunks, generate Gemini embeddings,
        and store chunks, embeddings, and metadata in PostgreSQL.
        """

        if not text or not text.strip():
            raise ValueError("Text cannot be empty.")

        if not file_name or not file_name.strip():
            raise ValueError("File name cannot be empty.")

        if not type or not type.strip():
            raise ValueError("Document type cannot be empty.")

        conn = None
        cur = None

        try:
            # --------------------------------
            # 1. Create chunks
            # --------------------------------

            chunks = create_chunks(
                text=text,
                chunk_size=2000,
                chunk_overlap=200,
            )

            if not chunks:
                raise ValueError("No chunks were created.")

            total_chunks = len(chunks)

            # --------------------------------
            # 2. Get database connection
            # --------------------------------

            conn, cur = get_db_connection()

            # --------------------------------
            # 3. Process every chunk
            # --------------------------------

            for chunk_index, chunk in enumerate(chunks):

                # Generate Gemini embedding
                embedding = generate_embedding(chunk)

                # Convert Python list into pgvector format
                embedding_string = "[" + ",".join(
                    str(value) for value in embedding
                ) + "]"

                # --------------------------------
                # Chunk metadata
                # --------------------------------

                metadata = {
                    "file_name": file_name,
                    "type": type,
                    "chunk_index": chunk_index,
                    "total_chunks": total_chunks,
                }

                # Convert metadata to JSON
                metadata_json = json.dumps(metadata)

                # --------------------------------
                # Store chunk + embedding + metadata
                # --------------------------------

                cur.execute(
                    """
                    INSERT INTO document (
                        original_text,
                        embedding_vector,
                        metadata
                    )
                    VALUES (
                        %s,
                        %s::vector,
                        %s::jsonb
                    )
                    """,
                    (
                        chunk,
                        embedding_string,
                        metadata_json,
                    ),
                )

            # --------------------------------
            # 4. Commit transaction
            # --------------------------------

            conn.commit()

            logger.debug(
                f"Successfully stored {total_chunks} chunks "
                f"for file '{file_name}'."
            )

            # --------------------------------
            # 5. Return result
            # --------------------------------

            return {
                "success": True,
                "file_name": file_name,
                "type": type,
                "number_of_chunks": total_chunks,
            }

        except Exception as e:

            if conn:
                conn.rollback()

            logger.exception(
                f"Failed to chunk and store document: {e}"
            )

            raise

        finally:

            # --------------------------------
            # 6. Release database connection
            # --------------------------------

            if conn:
                release_db_connection(conn, cur)


    @mcp.tool()
    def retrieve_top_chunks(
        query: str,
        top_n: int = 5,
    ) -> dict:
        """
        Retrieve the top N most relevant document chunks
        from PostgreSQL using pgvector cosine similarity.
        """
 
        if not query or not query.strip():
            raise ValueError("Query cannot be empty.")
 
        if top_n <= 0:
            raise ValueError("top_n must be greater than 0.")
 
        # Prevent unnecessarily large queries
        top_n = min(top_n, 20)
 
        conn = None
        cur = None
 
        try:
            logger.info(f"Retrieving top {top_n} chunks for query: {query[:100]}...")
 
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
                    1 - (embedding_vector <=> %s::vector) AS similarity
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
 
            chunks = []
 
            for row in rows:
                chunks.append({
                    "document_id": str(row[0]),
                    "text": row[1],
                    "metadata": row[2],
                    "created_at": row[3].isoformat() if row[3] else None,
                    "similarity_score": float(row[4]) if row[4] else 0.0,
                })
 
            logger.info(f"Retrieved {len(chunks)} chunks for query")
 
            # ================================
            # 4. RETURN RESULTS
            # ================================
 
            return {
                "success": True,
                "query": query,
                "chunks_found": len(chunks),
                "chunks": chunks,
            }
 
        except Exception as e:
            logger.exception(f"Failed to retrieve document chunks: {e}")
            raise
 
        finally:
            if conn:
                release_db_connection(conn, cur)