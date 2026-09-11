from uuid import UUID
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)


def get_invoice_by_id(invoice_id: UUID):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                invoice_id,
                customer_id,
                invoice_number,
                status,
                created_at
            FROM invoice
            WHERE invoice_id = %s
            """,
            (str(invoice_id),)
        )

        invoice = cur.fetchone()

        if not invoice:
            raise Exception(
                f"Invoice with id '{invoice_id}' not found"
            )

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, invoice))

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch invoice: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def create_new_invoice(
    customer_id: UUID,
    invoice_number: str,
    status: str = "draft",
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO invoice (
                customer_id,
                invoice_number,
                status
            )
            VALUES (%s, %s, %s)
            RETURNING
                invoice_id,
                customer_id,
                invoice_number,
                status,
                created_at
            """,
            (
                str(customer_id),
                invoice_number,
                status,
            )
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

        raise Exception(
            f"Failed to create invoice: {e}"
        )

    finally:
        release_db_connection(conn, cur)

def delete_invoice_by_id(invoice_id: UUID):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            DELETE FROM invoice
            WHERE invoice_id = %s
            RETURNING invoice_id
            """,
            (str(invoice_id),)
        )

        result = cur.fetchone()

        if not result:
            raise Exception(
                f"Invoice with id '{invoice_id}' not found"
            )

        conn.commit()

        return {
            "invoice_id": result[0],
            "message": "Invoice deleted successfully",
        }

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to delete invoice: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def get_orders_by_invoice_id(invoice_id: UUID):
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
            WHERE invoice_id = %s
            ORDER BY created_at DESC
            """,
            (str(invoice_id),)
        )

        orders = cur.fetchall()

        if not orders:
            raise Exception(
                f"No orders found for invoice '{invoice_id}'"
            )

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, order))
            for order in orders
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch orders for invoice: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def update_invoice_status_by_id(
    invoice_id: UUID,
    status: str,
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            UPDATE invoice
            SET
                status = %s
            WHERE invoice_id = %s
            RETURNING
                invoice_id,
                customer_id,
                invoice_number,
                status,
                created_at
            """,
            (
                status,
                str(invoice_id),
            )
        )

        invoice = cur.fetchone()

        if not invoice:
            raise Exception(
                f"Invoice with id '{invoice_id}' not found"
            )

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, invoice))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        raise Exception(
            f"Failed to update invoice status: {e}"
        )

    finally:
        release_db_connection(conn, cur)


def get_customer_invoices(customer_id: UUID):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                invoice_id,
                customer_id,
                invoice_number,
                status,
                created_at
            FROM invoice
            WHERE customer_id = %s
            ORDER BY created_at DESC
            """,
            (str(customer_id),)
        )

        invoices = cur.fetchall()

        if not invoices:
            raise Exception(
                f"No invoices found for customer '{customer_id}'"
            )

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, invoice))
            for invoice in invoices
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(
            f"Failed to fetch customer invoices: {e}"
        )

    finally:
        release_db_connection(conn, cur)
