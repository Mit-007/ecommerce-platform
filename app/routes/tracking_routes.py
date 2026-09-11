from fastapi import APIRouter, HTTPException
from uuid import UUID
from app.core.logger import logger
from app.model.tracking_event_routes_schema import CreateTrackingEvent
from app.database.repositories.order_repositories import tracking_order_by_id
from app.database.repositories.tracking_repositories import create_tracking_event

router = APIRouter(prefix="/orders",tags=["tracking order"])

@router.post("/{order_id}/tracking")
def create_order_tracking(order_id: UUID,data: CreateTrackingEvent):
    """
    create new tracking event for order.
    """
    try:
        tracking_event = create_tracking_event(
            order_id=order_id,
            status=data.status.value,
            location=data.location,
        )

        if tracking_event is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        return tracking_event

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while creating tracking event for order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create tracking event.",
        )


@router.get("/{order_id}/tracking")
def tracking_order(order_id: UUID):
    """
    list all track events for order.
    """
    try:
        tracking_event_list = tracking_order_by_id(order_id)

        if tracking_event_list is None:
            raise HTTPException(
                status_code=404,
                detail=f"Order with ID {order_id} not found.",
            )

        return tracking_event_list

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting tracking events for order {order_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve tracking events.",
        )