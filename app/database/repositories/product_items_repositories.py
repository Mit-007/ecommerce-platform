from psycopg2.extras import execute_values
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)
from uuid import UUID


def create_order_products_bulk(
    order_id: UUID,
    products_list: list[dict],
    returnable: bool = False,
):
    conn = cur = None

    try:
        if not products_list:
            raise ValueError("Products list cannot be empty.")

        conn, cur = get_db_connection()

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

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return [
            dict(zip(columns, product))
            for product in inserted_products
        ]

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to create order products: {e}"
        )

    finally:
        release_db_connection(conn, cur)