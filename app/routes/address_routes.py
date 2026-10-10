from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID
from app.database.repositories.address_repositories import (
    create_new_address,
    get_address_by_id,
    get_all_addresses_by_customer_id,
    get_latest_address_by_customer_id,
    update_address_by_id,
    delete_address_by_id,
)
from app.core.logger import logger
from app.model.address_routes_schema import (
    CreateAddress,
    UpdateAddress,
)
from app.dependencies.auth import get_current_customer

router = APIRouter(prefix="/address", tags=["address"])


@router.post("/")
def add_address(
    request: CreateAddress,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Create a new address for the authenticated customer.
    """
    try:
        customer_id = UUID(current_customer["customer_id"])

        address_data = create_new_address(
            customer_id=customer_id,
            full_name=request.full_name,
            phone=request.phone,
            address_line1=request.address_line1,
            address_line2=request.address_line2,
            city=request.city,
            state=request.state,
            postal_code=request.postal_code,
            country=request.country,
            is_default=request.is_default,
        )

        if address_data is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to create address.",
            )

        return address_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except ValueError as e:
        logger.error(f"Validation error while adding address: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while adding address: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/")
def get_user_addresses(
    current_customer: dict = Depends(get_current_customer),
):
    """
    Get all addresses for the authenticated customer.
    """
    try:
        customer_id = UUID(current_customer["customer_id"])
        addresses = get_all_addresses_by_customer_id(customer_id)
        return addresses

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching addresses for customer: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/latest")
def get_latest_address(
    current_customer: dict = Depends(get_current_customer),
):
    """
    Get the latest address for the authenticated customer.
    """
    try:
        customer_id = UUID(current_customer["customer_id"])
        address = get_latest_address_by_customer_id(customer_id)

        if address is None:
            raise HTTPException(
                status_code=404,
                detail="No address found for current customer.",
            )

        return address

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while fetching latest address: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{address_id}")
def get_address(
    address_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Get an address by ID for the authenticated customer.
    """
    try:
        address_data = get_address_by_id(address_id)

        if address_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Address with ID {address_id} not found.",
            )

        if str(address_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view addresses belonging to another customer.",
            )

        return address_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting address {address_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{address_id}")
def update_user_address(
    address_id: UUID,
    request: UpdateAddress,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Update an address for the authenticated customer.
    """
    try:
        address_data = get_address_by_id(address_id)

        if address_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Address with ID {address_id} not found.",
            )

        if str(address_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot update addresses belonging to another customer.",
            )

        customer_id = UUID(current_customer["customer_id"])
        update_dict = request.model_dump(exclude_unset=True)

        result = update_address_by_id(
            address_id=address_id,
            customer_id=customer_id,
            **update_dict,
        )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to update address.",
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
        logger.error(f"Error while updating address {address_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{address_id}")
def delete_user_address(
    address_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Delete an address for the authenticated customer.
    """
    try:
        address_data = get_address_by_id(address_id)

        if address_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Address with ID {address_id} not found.",
            )

        if str(address_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot delete addresses belonging to another customer.",
            )

        customer_id = UUID(current_customer["customer_id"])
        result = delete_address_by_id(
            address_id=address_id,
            customer_id=customer_id,
        )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete address.",
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
        logger.error(f"Error while deleting address {address_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
