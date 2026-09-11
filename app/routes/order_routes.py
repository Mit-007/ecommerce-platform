from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.database.repositories.order_repositories import (
    create_new_order,
    get_order_by_id,
    update_order_status_by_id,
    delete_order_by_id,
    list_products_by_id,
)
from app.database.repositories.product_items_repositories import (
    create_order_products_bulk,
)
from app.core.logger import logger
from app.model.order_routes_schema import (
    CreateOrder,
    OrderStatusUpdate,
)


router = APIRouter(prefix="/orders",tags=["orders"],)


@router.post("/")
def create_order(data: CreateOrder):
    """
    create new order.
    """
    try:
        order_data = create_new_order(
            data.customer_id,
            data.invoice_id,
            data.status,
            data.estimated_delivery_date,
        )

        if order_data is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to create order.",
            )

        order_id = order_data["order_id"]

        product_data = create_order_products_bulk(
            order_id,
            data.product_list,
            data.returnable,
        )

        return {
            "order_details": order_data,
            "products_item_details": product_data,
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
        logger.error(f"Error while creating order: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{order_id}")
def get_order(order_id: UUID):
    """
    fetch order from db using order id.
    """
    try:
        order_data = get_order_by_id(order_id)

        if order_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        return order_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting order: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{order_id}")
def update_order_status(
    order_id: UUID,
    request: OrderStatusUpdate,
):
    """
    order status change using a order id.
    """
    try:
        result = update_order_status_by_id(
            order_id,
            request.new_status,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
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
        logger.error(f"Error while updating order: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{order_id}")
def delete_order(order_id: UUID):
    """
    delete a order from databse.
    """
    try:
        result = delete_order_by_id(order_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
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
        logger.error(f"Error while deleting order: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{order_id}/items")
def list_order_products(order_id: UUID):
    """
    list all procucts of order.
    """
    try:
        product_list = list_products_by_id(order_id)

        if not product_list:
            raise HTTPException(
                status_code=404,
                detail=f"No products found for order with ID {order_id}.",
            )

        return product_list

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while listing order products: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )