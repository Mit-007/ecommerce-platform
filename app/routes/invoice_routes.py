from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from app.core.logger import logger
from app.database.repositories.invoice_repositories import (
    get_invoice_by_id,
    create_new_invoice,
    delete_invoice_by_id,
    get_orders_by_invoice_id,
    update_invoice_status_by_id,
    get_customer_invoices,
)
from app.model.invoice_routes_schema import (
    CreateInvoice,
    UpdateInvoiceStatus,
)
from app.dependencies.auth import get_current_customer

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Fetch invoice using invoice ID.
    Requires Bearer JWT access token.
    """
    try:
        invoice_data = get_invoice_by_id(invoice_id)

        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        if str(invoice_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You can only access your own invoices.",
            )

        return invoice_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while getting invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve invoice.",
        )


@router.post("/")
def create_invoice(
    request: CreateInvoice,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Create a new invoice in database.
    Requires Bearer JWT access token.
    """
    try:
        customer_id = UUID(current_customer["customer_id"])
        if request.customer_id and str(request.customer_id) != str(customer_id):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot create an invoice for another customer.",
            )

        invoice_data = create_new_invoice(
            customer_id=customer_id,
            invoice_number=request.invoice_number,
            status=request.status.value if hasattr(request.status, "value") else request.status,
        )

        if invoice_data is None:
            raise HTTPException(
                status_code=400,
                detail="Failed to create invoice.",
            )

        return invoice_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while creating invoice: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create invoice.",
        )


@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Delete an invoice from database.
    Requires Bearer JWT access token.
    """
    try:
        invoice_data = get_invoice_by_id(invoice_id)
        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        if str(invoice_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot delete invoices belonging to another customer.",
            )

        result = delete_invoice_by_id(invoice_id)

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete invoice.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while deleting invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to delete invoice.",
        )


@router.get("/{invoice_id}/orders")
def list_invoice_orders(
    invoice_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    List all orders for an invoice ID.
    Requires Bearer JWT access token.
    """
    try:
        invoice_data = get_invoice_by_id(invoice_id)
        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        if str(invoice_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot view orders for another customer's invoice.",
            )

        orders = get_orders_by_invoice_id(invoice_id)

        return orders if orders is not None else []

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while getting orders for invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve invoice orders.",
        )


@router.put("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: UUID,
    request: UpdateInvoiceStatus,
    current_customer: dict = Depends(get_current_customer),
):
    """
    Update invoice status.
    Requires Bearer JWT access token.
    """
    try:
        invoice_data = get_invoice_by_id(invoice_id)
        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        if str(invoice_data.get("customer_id")) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You cannot update status for another customer's invoice.",
            )

        result = update_invoice_status_by_id(
            invoice_id=invoice_id,
            status=request.status.value if hasattr(request.status, "value") else request.status,
        )

        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Failed to update invoice status.",
            )

        return result

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while updating invoice status {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update invoice status.",
        )


@router.get("/customer/{customer_id}")
def list_customer_invoices(
    customer_id: UUID,
    current_customer: dict = Depends(get_current_customer),
):
    """
    List all invoices for a customer.
    Requires Bearer JWT access token.
    """
    try:
        if str(customer_id) != str(current_customer["customer_id"]):
            raise HTTPException(
                status_code=403,
                detail="Access forbidden: You can only view your own invoices.",
            )

        invoices = get_customer_invoices(customer_id)

        return invoices if invoices is not None else []

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Database service temporarily unavailable.",
        )

    except Exception as e:
        logger.error(f"Error while getting invoices for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve customer invoices.",
        )
