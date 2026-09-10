import json
from uuid import UUID
from app.core.logger import logger
from app.database.connection import (
    get_db_connection,
    release_db_connection,
)


def get_conversation_by_id(conversation_id: UUID) -> dict | None:
    """
    Retrieve a conversation by conversation_id.

    Returns the conversation details including
    chat messages, or return None if the conversation
    does not exist.
    """

    conn = None
    cur = None

    try:
        logger.info(f"Retrieving conversation: {conversation_id}")

        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                conversation_id,
                customer_id,
                title,
                messages,
                created_at,
                updated_at
            FROM conversation
            WHERE conversation_id = %s
            """,
            (str(conversation_id),),
        )

        row = cur.fetchone()

        if not row:
            logger.warning(f"Conversation not found: {conversation_id}")
            return None

        logger.info(f"Conversation retrieved successfully: {conversation_id}")

        return row

    except Exception as e:
        logger.exception(f"Failed to retrieve conversation for {conversation_id}: {e}")
        raise

    finally:
        if conn:
            release_db_connection(conn, cur)


def append_conversation_messages(
    conversation_id: UUID,
    new_messages: list[dict],
) -> bool:
    """
    Append a new list of messages to the existing
    conversation messages.
    """

    conn = None
    cur = None

    try:
        conn, cur = get_db_connection()

        cur.execute(
            """
            UPDATE conversation
            SET
                messages = COALESCE(messages, '[]'::jsonb)
                           || %s::jsonb,
                updated_at = CURRENT_TIMESTAMP
            WHERE conversation_id = %s
            """,
            (
                json.dumps(new_messages),
                str(conversation_id),
            ),
        )

        if cur.rowcount == 0:
            conn.rollback()
            logger.warning(f"Conversation not found: {conversation_id}")
            return False

        conn.commit()

        logger.info(f"Successfully appended {len(new_messages)} messages to conversation: {conversation_id}")

        return True

    except Exception as e:
        if conn:
            conn.rollback()
            
        logger.exception(
            f"Failed to append messages to conversation {conversation_id}: {e}")
        raise

    finally:
        if conn:
            release_db_connection(conn, cur)


def get_all_conversations_by_customer(
    customer_id: UUID,
) -> list[dict]:
    """
    Retrieve all conversations for a customer.

    Conversations are ordered by updated_at DESC,
    so the most recently updated chat appears first.
    """

    conn = None
    cur = None

    try:
        logger.info(
            f"Retrieving conversations for customer: {customer_id}"
        )

        conn, cur = get_db_connection()

        cur.execute(
            """
            SELECT
                conversation_id,
                customer_id,
                title,
                messages,
                created_at,
                updated_at
            FROM conversation
            WHERE customer_id = %s
            ORDER BY updated_at DESC
            """,
            (str(customer_id),),
        )

        rows = cur.fetchall()

        conversations = []

        for row in rows:
            conversations.append({
                "conversation_id": str(row[0]),
                "customer_id": str(row[1]),
                "title": row[2],
                "messages": row[3],
                "created_at": row[4].isoformat(),
                "updated_at": row[5].isoformat(),
            })

        logger.info(
            f"Retrieved {len(conversations)} conversations "
            f"for customer: {customer_id}"
        )

        return conversations

    except Exception as e:
        logger.exception(
            f"Failed to retrieve conversations "
            f"for customer {customer_id}: {e}"
        )
        raise

    finally:
        if conn:
            release_db_connection(conn, cur)


def create_new_conversation(
    customer_id: UUID,
    title: str | None = None,
) -> UUID:

    conn = None
    cur = None

    try:
        logger.info(
            f"Creating new conversation for customer: {customer_id}"
        )

        conn, cur = get_db_connection()

        cur.execute(
            """
            INSERT INTO conversation (
                customer_id,
                title
            )
            VALUES (%s, %s)
            RETURNING
                conversation_id, 
                customer_id, 
                title, 
                messages, 
                created_at, 
                updated_at
            """,
            (
                str(customer_id),
                title,
            ),
        )

        new_conversation= cur.fetchone()

        conn.commit()

        logger.info(
            f"New conversation created successfully: {new_conversation[0]}"
        )

        return new_conversation

    except Exception as e:

        if conn:
            conn.rollback()

        logger.exception(
            f"Failed to create new conversation "
            f"for customer {customer_id}: {e}"
        )

        raise

    finally:

        if conn:
            release_db_connection(conn, cur)