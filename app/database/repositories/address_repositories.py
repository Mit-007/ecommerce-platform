from uuid import UUID
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)


def create_new_address(
    customer_id: UUID,
    full_name: str,
    phone: str,
    address_line1: str,
    city: str,
    state: str,
    postal_code: str,
    address_line2: str | None = None,
    country: str = "India",
    is_default: bool = False,
) -> dict:
    """
    Create a new address for a customer.
    If is_default is True, reset any existing default addresses for this customer.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        if is_default:
            cur.execute(
                """
                UPDATE address
                SET is_default = FALSE
                WHERE customer_id = %s AND is_default = TRUE
                """,
                (str(customer_id),),
            )

        cur.execute(
            """
            INSERT INTO address (
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
                address_id,
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
                created_at,
                updated_at
            """,
            (
                str(customer_id),
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
            ),
        )

        address = cur.fetchone()
        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, address))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to create address: {e}")

    finally:
        release_db_connection(conn, cur)


def get_address_by_id(address_id: UUID) -> dict | None:
    """
    Fetch an address by address_id.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                address_id,
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
                created_at,
                updated_at
            FROM address
            WHERE address_id = %s
            """,
            (str(address_id),),
        )

        address = cur.fetchone()

        if not address:
            return None

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, address))

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch address: {e}")

    finally:
        release_db_connection(conn, cur)


def get_all_addresses_by_customer_id(customer_id: UUID) -> list[dict]:
    """
    Fetch all addresses belonging to a specific customer.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                address_id,
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
                created_at,
                updated_at
            FROM address
            WHERE customer_id = %s
            ORDER BY is_default DESC, created_at DESC
            """,
            (str(customer_id),),
        )

        addresses = cur.fetchall()

        if not addresses:
            return []

        columns = [desc[0] for desc in cur.description]

        return [
            dict(zip(columns, addr))
            for addr in addresses
        ]

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch customer addresses: {e}")

    finally:
        release_db_connection(conn, cur)


def get_latest_address_by_customer_id(customer_id: UUID) -> dict | None:
    """
    Fetch the latest address created for a customer.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                address_id,
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
                created_at,
                updated_at
            FROM address
            WHERE customer_id = %s
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (str(customer_id),),
        )

        address = cur.fetchone()

        if not address:
            return None

        columns = [desc[0] for desc in cur.description]

        return dict(zip(columns, address))

    except ConnectionError:
        raise

    except Exception as e:
        raise Exception(f"Failed to fetch latest customer address: {e}")

    finally:
        release_db_connection(conn, cur)


def update_address_by_id(
    address_id: UUID,
    customer_id: UUID,
    **fields,
) -> dict | None:
    """
    Update an address by address_id for a given customer.
    If is_default is set to True, resets default flag on other addresses of the customer.
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        if fields.get("is_default") is True:
            cur.execute(
                """
                UPDATE address
                SET is_default = FALSE
                WHERE customer_id = %s AND address_id != %s AND is_default = TRUE
                """,
                (str(customer_id), str(address_id)),
            )

        allowed_fields = [
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
        ]

        set_clauses = []
        values = []

        for key in allowed_fields:
            if key in fields and fields[key] is not None:
                set_clauses.append(f"{key} = %s")
                values.append(fields[key])

        if not set_clauses:
            return get_address_by_id(address_id)

        values.extend([str(address_id), str(customer_id)])

        query = f"""
            UPDATE address
            SET {', '.join(set_clauses)}, updated_at = CURRENT_TIMESTAMP
            WHERE address_id = %s AND customer_id = %s
            RETURNING
                address_id,
                customer_id,
                full_name,
                phone,
                address_line1,
                address_line2,
                city,
                state,
                postal_code,
                country,
                is_default,
                created_at,
                updated_at
        """

        cur.execute(query, tuple(values))

        address = cur.fetchone()

        if not address:
            return None

        columns = [desc[0] for desc in cur.description]

        conn.commit()

        return dict(zip(columns, address))

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to update address: {e}")

    finally:
        release_db_connection(conn, cur)


def delete_address_by_id(
    address_id: UUID,
    customer_id: UUID | None = None,
) -> dict | None:
    """
    Delete an address by address_id (and optionally customer_id for safety).
    """
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        if customer_id:
            cur.execute(
                """
                DELETE FROM address
                WHERE address_id = %s AND customer_id = %s
                RETURNING address_id
                """,
                (str(address_id), str(customer_id)),
            )
        else:
            cur.execute(
                """
                DELETE FROM address
                WHERE address_id = %s
                RETURNING address_id
                """,
                (str(address_id),),
            )

        result = cur.fetchone()

        if not result:
            return None

        conn.commit()

        return {
            "address_id": result[0],
            "message": "Address deleted successfully",
        }

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Failed to delete address: {e}")

    finally:
        release_db_connection(conn, cur)
