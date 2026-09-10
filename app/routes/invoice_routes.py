from uuid import UUID
from fastapi import APIRouter, HTTPException
from app.core.logger import logger
from app.database.repositories.invoice_repositories import (
    get_invoice_by_id,
    create_new_invoice,
    update_invoice_by_id,
    delete_invoice_by_id,
    get_orders_by_invoice_id,
    update_invoice_status_by_id,
    get_customer_invoices,
)
from app.model.invoice_routes_schema import (
    CreateInvoice,
    UpdateInvoice,
    UpdateInvoiceStatus,
)

router = APIRouter(prefix="/invoices",tags=["invoices"])

@router.get("/{invoice_id}")
def get_invoice(invoice_id: UUID):
    try:
        invoice_data = get_invoice_by_id(invoice_id)

        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        return invoice_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/")
def create_invoice(request: CreateInvoice):
    try:
        invoice_data = create_new_invoice(
            customer_id=request.customer_id,
            invoice_number=request.invoice_number,
            status=request.status.value,
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
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while creating invoice: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{invoice_id}")
def update_invoice(
    invoice_id: UUID,
    request: UpdateInvoice,
):
    try:
        invoice_data = update_invoice_by_id(
            invoice_id=invoice_id,
            invoice_number=request.invoice_number,
            status=request.status.value,
        )

        if invoice_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        return invoice_data

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while updating invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: UUID):
    try:
        result = delete_invoice_by_id(invoice_id)

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
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
        logger.error(f"Error while deleting invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/{invoice_id}/orders")
def list_invoice_orders(invoice_id: UUID):
    try:
        orders = get_orders_by_invoice_id(invoice_id)

        if orders is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
            )

        return orders

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting orders for invoice {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.put("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: UUID,
    request: UpdateInvoiceStatus,
):
    try:
        result = update_invoice_status_by_id(
            invoice_id=invoice_id,
            status=request.status.value,
        )

        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"Invoice with ID {invoice_id} not found.",
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
        logger.error(f"Error while updating invoice status {invoice_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.get("/customer/{customer_id}")
def list_customer_invoices(customer_id: UUID):
    try:
        invoices = get_customer_invoices(customer_id)

        if invoices is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with ID {customer_id} not found.",
            )

        return invoices

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while getting invoices for customer {customer_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
