from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_customer

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.get("/")
def get_my_orders(
    customer_id: str = Depends(get_current_customer)
):
    return {
        "customer_id": customer_id,
        "message": "Get customer's orders"
    }