from server.database.connection import get_db_connection,release_db_connection

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