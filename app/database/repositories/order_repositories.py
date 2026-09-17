from app.database.connection import get_db_connection,release_db_connection
from psycopg2.extras import execute_values
from uuid import UUID

def create_order_with_products(
    customer_id: UUID,
    invoice_id: UUID,
    products_list: list,
    status: str = "pending",
    estimated_delivery_date=None,
    returnable: bool = False,
):
    conn = cur = None

    try:
        if not products_list:
            raise ValueError("Products list cannot be empty.")

        conn, cur = get_db_connection()

        # 1. Create Order
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
            ),
        )

        order = cur.fetchone()
        order_columns = [desc[0] for desc in cur.description]

        order_data = dict(zip(order_columns, order))

        order_id = order_data["order_id"]

        # 2. Create Order Products
        query = """
            INSERT INTO product_item (
                order_id,
                name,
                quantity,
                returnable
            )
            VALUES %s
            RETURNING
                product_item_id,
                order_id,
                name,
                quantity,
                returnable,
                created_at
        """

        values = [
            (
                str(order_id),
                product.name,
                product.quantity,
                returnable,
            )
            for product in products_list
        ]

        inserted_products = execute_values(
            cur,
            query,
            values,
            fetch=True,
        )

        product_columns = [desc[0] for desc in cur.description]

        product_data = [
            dict(zip(product_columns, product))
            for product in inserted_products
        ]

        # 3. Commit Both Operations
        conn.commit()

        return order_data,product_data 

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to create order with products: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def get_order_by_id(order_id: UUID):
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
            (str(order_id),)
        )

        order = cur.fetchone()

        if not order:
            return None

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
    order_id: UUID,
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
                str(order_id),
            )
        )

        order = cur.fetchone()

        if not order:
            return None

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


def delete_order_by_id(order_id: UUID):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            DELETE FROM orders
            WHERE order_id = %s
            RETURNING order_id
            """,
            (str(order_id),)
        )

        result = cur.fetchone()

        if not result:
            return None

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
            return None

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
            return None

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