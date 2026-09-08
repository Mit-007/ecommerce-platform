from server.database.connection import get_db_connection ,release_db_connection

def get_order_by_id(order_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                order_id,
                customer_id,
                invoice_id,
                status,
                estimated_delivery_date,
                created_at,
                updated_at
            FROM orders
            WHERE order_id = %s
            """,
            (order_id,)
        )

        order = cur.fetchone()

        if not order:
            raise ValueError(f"Order not found: {order_id}")

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, order))

    except ConnectionError:
        raise

    except ValueError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to fetch order: {e}")

    finally:
        release_db_connection(conn, cur)


def list_order_items(order_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                product_item_id,
                order_id,
                name,
                quantity,
                returnable,
                created_at
            FROM product_item
            WHERE order_id = %s
            ORDER BY created_at ASC
            """,
            (order_id,)
        )

        items = cur.fetchall()

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, item))
            for item in items
        ]

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to fetch order items: {e}")

    finally:
        release_db_connection(conn, cur)

def track_order_by_id(order_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                tracking_event_id,
                order_id,
                status,
                location,
                timestamp
            FROM tracking_event
            WHERE order_id = %s
            ORDER BY timestamp ASC
            """,
            (order_id,)
        )

        tracking_events = cur.fetchall()

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, event))
            for event in tracking_events
        ]

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to track order: {e}")

    finally:
        release_db_connection(conn, cur)

def cancel_order_by_id(order_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            UPDATE orders
            SET
                status = 'cancelled',
                updated_at = CURRENT_TIMESTAMP
            WHERE order_id = %s
            RETURNING
                order_id,
                customer_id,
                invoice_id,
                status,
                estimated_delivery_date,
                created_at,
                updated_at
            """,
            (order_id,)
        )

        order = cur.fetchone()

        if not order:
            raise ValueError(f"Order not found: {order_id}")

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, order))

    except ConnectionError:
        raise

    except ValueError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to cancel order: {e}")

    finally:
        release_db_connection(conn, cur)

def create_support_ticket_by_order_id(
    order_id: str,
    summary: str,
    conversation_id: str | None = None
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO support_ticket (
                order_id,
                conversation_id,
                summary
            )
            VALUES (%s, %s, %s)
            RETURNING
                support_ticket_id,
                order_id,
                conversation_id,
                summary,
                status,
                human_response,
                created_at,
                updated_at
            """,
            (
                order_id,
                conversation_id,
                summary
            )
        )

        ticket = cur.fetchone()

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, ticket))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to create support ticket: {e}")

    finally:
        release_db_connection(conn, cur)

def get_support_ticket_by_id(support_ticket_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                support_ticket_id,
                order_id,
                conversation_id,
                summary,
                status,
                human_response,
                created_at,
                updated_at
            FROM support_ticket
            WHERE support_ticket_id = %s
            """,
            (support_ticket_id,)
        )

        ticket = cur.fetchone()

        if not ticket:
            raise ValueError(
                f"Support ticket not found: {support_ticket_id}"
            )

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, ticket))

    except ConnectionError:
        raise

    except ValueError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(f"Failed to fetch support ticket: {e}")

    finally:
        release_db_connection(conn, cur)