from fastapi import APIRouter, HTTPException ,Depends
from uuid import UUID
from app.database.repositories.order_repositories import (
    create_order_with_products,
    get_order_by_id,
    update_order_status_by_id,
    delete_order_by_id,
    list_products_by_id,
)
from app.core.logger import logger
from app.model.order_routes_schema import (
    CreateOrder,
    OrderStatusUpdate,
)
from app.dependencies.auth import get_current_customer


router = APIRouter(prefix="/orders",tags=["orders"],)


@router.post("/")
def create_order(request: CreateOrder,current_customer: dict = Depends(get_current_customer)):
    """
    create new order.
    """
    try:
        customer_id = UUID(current_customer["customer_id"])
        if request.customer_id and str(request.customer_id) != str(customer_id):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot create an order for another customer.",
            )

        order_data,product_data = create_order_with_products(
            customer_id=request.customer_id,
            invoice_id=request.invoice_id,
            status=request.status.value if hasattr(request.status, "value") else request.status,
            estimated_delivery_date=request.estimated_delivery_date,
            products_list=request.product_list,
            returnable=request.returnable,
        )

        if order_data is None or product_data is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to create order.",
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
def get_order(order_id: UUID,current_customer: dict = Depends(get_current_customer)):
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

        if str(order_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view order items belonging to another customer.",
            )
        
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
    current_customer: dict = Depends(get_current_customer)
):
    """
    order status change using a order id.
    """
    try:
        order_data = get_order_by_id(order_id)
        if order_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        if str(order_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view order items belonging to another customer.",
            )
        
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
def delete_order(order_id: UUID,current_customer: dict = Depends(get_current_customer)):
    """
    delete a order from databse.
    """
    try:
        order_data = get_order_by_id(order_id)
        if order_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        if str(order_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view order items belonging to another customer.",
            )
        
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
def list_order_products(order_id: UUID,current_customer: dict = Depends(get_current_customer)):
    """
    list all procucts of order.
    """
    try:
        order_data = get_order_by_id(order_id)
        if order_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        if str(order_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view order items belonging to another customer.",
            )
        
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