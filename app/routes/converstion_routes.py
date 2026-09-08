from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.core.logger import logger
from app.database.repositories.converstion_repositories import (
    get_all_conversations_by_customer,
)

router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"],
)


@router.get("/{customer_id}")
def get_customer_conversations(customer_id: UUID):
    """
    Get all conversations for a customer.

    Conversations are ordered by latest updated chat first.
    """

    try:
        conversations = get_all_conversations_by_customer(
            customer_id=customer_id
        )

        return {
            "customer_id": str(customer_id),
            "conversations": conversations,
        }

    except Exception as e:
        logger.exception(
            f"Failed to retrieve conversations "
            f"for customer: {customer_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve conversations.",
        )