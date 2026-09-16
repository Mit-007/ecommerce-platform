import asyncio
from fastmcp import FastMCP
from server.core.logger import logger
from server.models.tool_input_schema import GetOrderRequest
from server.models.tool_output_schema import ToolResponse
from server.database.repositories.order_tool_repositories import (
    get_order_by_id,
    track_order_by_id,
    cancel_order_by_id,
    list_order_items_by_order_id,
)


def register_order_tools(mcp: FastMCP) -> None:
    """Register order management tools with MCP server"""

    @mcp.tool()
    async def get_order(request: GetOrderRequest) -> ToolResponse:
        """
        Retrieve complete order details including current status, customer information,
        invoice reference, and estimated delivery date.
        """
        logger.info(
            f"Executing get_order with order_id={request.order_id}"
        )

        try:
            result = await asyncio.to_thread(
                get_order_by_id,
                request.order_id,
            )

            if not result:
                logger.warning(
                    f"Order not found: {request.order_id}"
                )
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found",
                )

            logger.info(
                f"Successfully retrieved order {request.order_id}"
            )

            return ToolResponse(
                success=True,
                data=result,
                error=None,
            )

        except ValueError as e:
            logger.warning(
                f"ValueError in get_order: {str(e)}"
            )
            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in get_order: {str(e)}",
                exc_info=True,
            )
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed",
            )

    @mcp.tool()
    async def list_order_items(
        request: GetOrderRequest,
    ) -> ToolResponse:
        """
        Retrieve all product items associated with a specific order.
        """

        logger.info(
            f"Executing list_order_items with order_id={request.order_id}"
        )

        try:
            result = await asyncio.to_thread(
                list_order_items_by_order_id,
                request.order_id,
            )

            if result is None:
                result = []

            logger.info(
                f"Successfully retrieved {len(result)} items "
                f"for order {request.order_id}"
            )

            return ToolResponse(
                success=True,
                data=result,
                error=None,
            )

        except ValueError as e:
            logger.warning(
                f"ValueError in list_order_items: {str(e)}"
            )
            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in list_order_items: {str(e)}",
                exc_info=True,
            )
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed",
            )

    @mcp.tool()
    async def track_order(
        request: GetOrderRequest,
    ) -> ToolResponse:
        """
        Track real-time delivery status and location of an order.
        """

        logger.info(
            f"Executing track_order with order_id={request.order_id}"
        )

        try:
            result = await asyncio.to_thread(
                track_order_by_id,
                request.order_id,
            )

            if result is None:
                result = []

            logger.info(
                f"Successfully retrieved tracking info "
                f"for order {request.order_id}"
            )

            return ToolResponse(
                success=True,
                data=result,
                error=None,
            )

        except ValueError as e:
            logger.warning(
                f"ValueError in track_order: {str(e)}"
            )
            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in track_order: {str(e)}",
                exc_info=True,
            )
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed",
            )

    @mcp.tool()
    async def cancel_order(
        request: GetOrderRequest,
    ) -> ToolResponse:
        """
        Cancel a pending order and update its status to 'cancelled'.
        """

        logger.info(
            f"Executing cancel_order with order_id={request.order_id}"
        )

        try:
            # Retrieve current order status
            order = await asyncio.to_thread(
                get_order_by_id,
                request.order_id,
            )

            if not order:
                logger.warning(
                    f"Order not found: {request.order_id}"
                )
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found",
                )

            order_status = order.get("status", "").lower()

            # Check if order is already cancelled
            if order_status == "cancelled":
                logger.warning(
                    f"Order already cancelled: {request.order_id}"
                )
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order is already cancelled",
                )

            # Check if order is pending
            if order_status != "pending":
                logger.warning(
                    f"Order not in pending status for cancellation: "
                    f"{request.order_id} (status: {order_status})"
                )

                return ToolResponse(
                    success=False,
                    data=None,
                    error=(
                        f"Order cannot be cancelled. "
                        f"Current status is '{order_status}'. "
                        f"Only pending orders can be cancelled. "
                        f"Please contact support for further assistance"
                    ),
                )

            # Perform cancellation
            result = await asyncio.to_thread(
                cancel_order_by_id,
                request.order_id,
            )

            if not result:
                logger.error(
                    f"Failed to cancel order: {request.order_id}"
                )
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Failed to cancel order",
                )

            logger.info(
                f"Successfully cancelled order {request.order_id}"
            )

            return ToolResponse(
                success=True,
                data=result,
                error=None,
            )

        except ValueError as e:
            logger.warning(
                f"ValueError in cancel_order: {str(e)}"
            )
            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in cancel_order: {str(e)}",
                exc_info=True,
            )
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed",
            )