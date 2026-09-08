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
                chunk_size=1000,
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