from fastapi import APIRouter
from uuid import UUID
from app.database.repositories.order_repositories import tracking_order_by_id
from app.core.logger import logger
from fastapi import APIRouter, HTTPException
from app.model.tracking_event_routes_schema import CreateTrackingEvent
from app.database.repositories.tracking_repositories import create_tracking_event
router = APIRouter(prefix="/orders", tags=["tracking order"])

@router.post("/{order_id}/tracking")
def create_order_tracking(
    order_id: UUID,
    data: CreateTrackingEvent,
):
    try:
        tracking_event = create_tracking_event(
            order_id=order_id,
            status=data.status.value,
            location=data.location,
        )

        return tracking_event

    except Exception as e:
        logger.exception(
            f"Failed to create tracking event "
            f"for order {order_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create tracking event",
        )


@router.get("/{order_id}/tracking")
def traking_order(order_id: UUID):
    try:
        tracking_event_list = tracking_order_by_id(order_id)
        return tracking_event_list
    
    except Exception as e:
        logger.error(e)
        return {
            "message" : "not get tracking events !!"
        } 