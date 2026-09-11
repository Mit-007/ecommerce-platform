from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.model.auth_routes_schema import ChangePassword
from app.database.repositories.customer_repositories import (
    update_customer_password,
    delete_customer_by_id,
    get_customer_by_id,
)
from app.core.logger import logger

router = APIRouter(prefix="/customer",tags=["customer"])


@router.get("/{customer_id}")
def get_customer(customer_id: UUID):
    """
    fetch customer details using id.
    """
    try:
        customer_data = get_customer_by_id(customer_id)

        if customer_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return customer_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting customer: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{customer_id}")
def change_customer_password(customer_id: UUID, request:ChangePassword):
    """
    change a customer password.
    """
    try:
        result = update_customer_password(
            customer_id,
            request.new_password,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while updating customer password: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{customer_id}")
def delete_customer(customer_id: UUID):
    """
    delete a customer profile.
    """
    try:
        result = delete_customer_by_id(customer_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while deleting customer: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )