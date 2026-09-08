from app.database.connection import get_db_connection,release_db_connection
from uuid import UUID

def create_new_order(
    customer_id: UUID,
    invoice_id: UUID,
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
                str(customer_id),
                str(invoice_id),
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
            raise Exception(
                f"Order with id '{order_id}' not found"
            )

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, order))

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch order: {e}"
        )

    finally:
        release_db_connection(conn, cur)



def update_order_status_by_id(
    order_id: str,
    status: str,
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            UPDATE orders
            SET
                status = %s,
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
            (
                status,
                order_id,
            )
        )

        order = cur.fetchone()

        if not order:
            raise Exception(
                f"Order with id '{order_id}' not found"
            )

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, order))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to update order status: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def delete_order_by_id(order_id: str):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            DELETE FROM orders
            WHERE order_id = %s
            RETURNING order_id
            """,
            (order_id,)
        )

        result = cur.fetchone()

        if not result:
            raise Exception(
                f"Order with id '{order_id}' not found"
            )

        conn.commit()

        return {
            "order_id": result[0],
            "message": "Order deleted successfully",
        }

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to delete order: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def tracking_order_by_id(order_id: UUID):
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
            (str(order_id),)
        )

        tracking_events = cur.fetchall()

        if not tracking_events:
            raise Exception(
                f"No tracking events found for order '{order_id}'"
            )

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, event))
            for event in tracking_events
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch tracking information: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def list_products_by_id(order_id: UUID):
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
            (str(order_id),)
        )

        products = cur.fetchall()

        if not products:
            raise Exception(
                f"No products found for order '{order_id}'"
            )

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, product))
            for product in products
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch products for order: {e}"
        )

    finally:
        release_db_connection(conn, cur)