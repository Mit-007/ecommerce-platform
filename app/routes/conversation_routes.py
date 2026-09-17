from fastapi import APIRouter, HTTPException ,Depends
from uuid import UUID
from app.core.logger import logger
from app.database.repositories.conversation_repositories import (
    get_all_conversations_by_customer,
)
from app.dependencies.auth import get_current_customer

router = APIRouter(prefix="/customer",tags=["conversation"])


@router.get("/{customer_id}/conversations")
def get_customer_conversations(
    customer_id: UUID,
    current_customer: dict = Depends(get_current_customer),
    ):
    """
    Get all conversations for a customer.
    Conversations are ordered by latest updated chat first.
    """
    try:
        if str(customer_id) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You not have an access",
            )

        conversations = get_all_conversations_by_customer(customer_id=customer_id)

        if conversations is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return {
            "customer_id": str(customer_id),
            "conversations": conversations,
        }

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while retrieving conversations :{e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )