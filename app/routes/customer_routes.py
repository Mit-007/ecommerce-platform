from fastapi import APIRouter, HTTPException,Depends
from uuid import UUID
from app.model.auth_routes_schema import ChangePassword
from app.database.repositories.customer_repositories import (
    update_customer_password,
    delete_customer_by_id,
    get_customer_by_id,
)
from app.core.logger import logger
from app.dependencies.auth import get_current_customer

router = APIRouter(prefix="/customer",tags=["customer"])


@router.get("/{customer_id}")
def get_customer(customer_id: UUID,current_customer: dict = Depends(get_current_customer)):
    """
    fetch customer details using id.
    """
    try:
        if str(customer_id) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You can only access your own profile.",
            )

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
def change_customer_password(customer_id: UUID, request:ChangePassword,current_customer: dict = Depends(get_current_customer)):
    """
    change a customer password.
    """
    try:
        if str(customer_id) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You can not change other customer profile password.",
            )

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
def delete_customer(customer_id: UUID,current_customer: dict = Depends(get_current_customer)):
    """
    delete a customer profile.
    """
    try:
        if str(customer_id) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You can only delete your own profile.",
            )
        
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