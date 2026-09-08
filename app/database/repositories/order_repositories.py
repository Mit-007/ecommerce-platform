from app.database.connection import get_db_connection,release_db_connection

def create_order(
    customer_id: str,
    invoice_id: str,
    status: str = "pending",
    estimated_delivery_date=None,
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO orders (
                customer_id,
                invoice_id,
                status,
                estimated_delivery_date
            )
            VALUES (%s, %s, %s, %s)
            RETURNING
                order_id,
                customer_id,
                invoice_id,
                status,
                estimated_delivery_date,
                created_at,
                updated_at
            """,
            (
                customer_id,
                invoice_id,
                status,
                estimated_delivery_date,
            )
        )

        order = cur.fetchone()

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, order))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to create order: {e}")

    finally:
        release_db_connection(conn, cur)