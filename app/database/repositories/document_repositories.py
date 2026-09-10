import json
from psycopg2.extras import execute_values
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)


def store_documents_bulk(
    documents_list: list[dict],
):
    conn = cur = None

    try:
        if not documents_list:
            raise ValueError(
                "Documents list cannot be empty."
            )

        conn, cur = get_db_connection()

        query = """
            INSERT INTO document (
                original_text,
                embedding_vector,
                metadata
            )
            VALUES %s
            RETURNING
                document_id,
                original_text,
                embedding_vector,
                metadata,
                created_at;
        """

        values = [
            (
                document["text"],
                "[" + ",".join(
                    str(value)
                    for value in document["embedding"]
                ) + "]",
                json.dumps(document["metadata"]),
            )
            for document in documents_list
        ]

        inserted_documents = execute_values(
            cur,
            query,
            values,
            template="(%s, %s::vector, %s::jsonb)",
            fetch=True,
        )

        columns = [
            desc[0]
            for desc in cur.description
        ]

        conn.commit()

        return [
            dict(zip(columns, document))
            for document in inserted_documents
        ]

    except ConnectionError:
        raise

    except Exception as e:

        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to store documents: {e}"
        )

    finally:
        release_db_connection(conn, cur)
