from uuid import UUID
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)
from app.core.logger import logger


def create_tracking_event(
    order_id: UUID,
    status: str,
    location: str | None = None,
):
    conn = cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO tracking_event (
                order_id,
                status,
                location
            )
            VALUES (%s, %s, %s)
            RETURNING
                tracking_event_id,
                order_id,
                status,
                location,
                timestamp
            """,
            (
                str(order_id),
                status,
                location,
            ),
        )

        tracking_event = cur.fetchone()

        if not tracking_event:
            raise Exception(
                "Failed to create tracking event."
            )

        columns = [
            description[0]
            for description in cur.description
        ]

        conn.commit()

        return dict(
            zip(columns, tracking_event)
        )

    except ConnectionError:
        raise

    except Exception as e:
        if conn:
            conn.rollback()

        logger.exception(
            f"Failed to create tracking event "
            f"for order {order_id}: {e}"
        )

        raise Exception(
            f"Failed to create tracking event: {e}"
        )

    finally:
        if conn:
            release_db_connection(conn, cur)