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

router = APIRouter(prefix="/invoices",tags=["invoices"],)


@router.get("/{invoice_id}")
def get_invoice(invoice_id: UUID):
    try:
        invoice_data = get_invoice_by_id(invoice_id)

        return invoice_data

    except Exception as e:
        logger.exception(
            f"Failed to get invoice {invoice_id}: {e}"
        )

        raise HTTPException(
            status_code=404,
            detail="Invoice not found",
        )


@router.post("/")
def create_invoice(data: CreateInvoice):
    try:
        invoice_data = create_new_invoice(
            customer_id=data.customer_id,
            invoice_number=data.invoice_number,
            status=data.status.value,
        )

        return invoice_data

    except Exception as e:
        logger.exception(
            f"Failed to create invoice: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to create invoice",
        )


@router.put("/{invoice_id}")
def update_invoice(
    invoice_id: UUID,
    data: UpdateInvoice,
):
    try:
        invoice_data = update_invoice_by_id(
            invoice_id=invoice_id,
            invoice_number=data.invoice_number,
            status=data.status.value,
        )

        return invoice_data

    except Exception as e:
        logger.exception(
            f"Failed to update invoice {invoice_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update invoice",
        )


@router.delete("/{invoice_id}")
def delete_invoice(invoice_id: UUID):
    try:
        result = delete_invoice_by_id(invoice_id)

        return result

    except Exception as e:
        logger.exception(
            f"Failed to delete invoice {invoice_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to delete invoice",
        )


@router.get("/{invoice_id}/orders")
def list_invoice_orders(invoice_id: UUID):
    try:
        orders = get_orders_by_invoice_id(invoice_id)

        return orders

    except Exception as e:
        logger.exception(
            f"Failed to get orders for invoice {invoice_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to get orders for invoice",
        )


@router.put("/{invoice_id}/status")
def update_invoice_status(
    invoice_id: UUID,
    data: UpdateInvoiceStatus,
):
    try:
        result = update_invoice_status_by_id(
            invoice_id=invoice_id,
            status=data.status.value,
        )

        return result

    except Exception as e:
        logger.exception(
            f"Failed to update invoice status {invoice_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to update invoice status",
        )


@router.get("/customer/{customer_id}")
def list_customer_invoices(customer_id: UUID):
    try:
        invoices = get_customer_invoices(customer_id)

        return invoices

    except Exception as e:
        logger.exception(
            f"Failed to get invoices for customer {customer_id}: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to get customer invoices",
        )