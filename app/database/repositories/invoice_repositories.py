from app.database.connection import get_db_connection,release_db_connection

def create_invoice(invoice_number: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO invoice (
                invoice_number
            )
            VALUES (%s)
            RETURNING
                invoice_id,
                invoice_number,
                status,
                created_at
            """,
            (invoice_number,)
        )

        invoice = cur.fetchone()

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, invoice))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to create invoice: {e}")

    finally:
        release_db_connection(conn, cur)