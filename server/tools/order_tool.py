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


def register_document_tools(mcp: FastMCP) -> None:
    """Register order management tools with MCP server"""

    @mcp.tool()
    def get_order(request: GetOrderRequest) -> ToolResponse:
        """
        Retrieve complete order details including current status, customer information, invoice reference, 
        and estimated delivery date. This tool returns the full order record from the orders table 
        with all current order metadata and state information.
        
        Args:
            request: GetOrderRequest containing order_id (UUID)
            
        Returns:
            ToolResponse containing order data with fields: order_id, customer_id, invoice_id, 
            status (pending/processing/shipped/delivered/cancelled/returned), estimated_delivery_date, 
            created_at, updated_at
        """
        logger.info(f"Executing get_order with order_id={request.order_id}")
        
        try:
            if not request or not request.order_id:
                logger.warning("Invalid order_id provided to get_order")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Invalid order ID provided"
                )
            
            result = get_order_by_id(request.order_id)
            
            if not result:
                logger.warning(f"Order not found: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found"
                )
            
            logger.info(f"Successfully retrieved order {request.order_id}")
            return ToolResponse(
                success=True,
                data=result,
                error=None
            )
            
        except ValueError as e:
            logger.warning(f"ValueError in get_order: {str(e)}")
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in get_order: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed"
            )

    @mcp.tool()
    def list_order_items(request: GetOrderRequest) -> ToolResponse:
        """
        Retrieve all product items associated with a specific order. Returns a list of items 
        from the product_item table filtered by order_id. Each item includes product name, 
        quantity ordered, and whether the item is returnable. Use this to view the complete 
        contents and composition of an order.
        
        Args:
            request: GetOrderRequest containing order_id (UUID)
            
        Returns:
            ToolResponse containing list of product items with fields: product_item_id, 
            name, quantity, returnable, created_at
        """
        logger.info(f"Executing list_order_items with order_id={request.order_id}")
        
        try:
            if not request or not request.order_id:
                logger.warning("Invalid order_id provided to list_order_items")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Invalid order ID provided"
                )
            
            # Verify order exists first
            order = get_order_by_id(request.order_id)
            if not order:
                logger.warning(f"Order not found: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found"
                )
            
            result = list_order_items_by_order_id(request.order_id)
            
            if result is None:
                result = []
            
            logger.info(f"Successfully retrieved {len(result)} items for order {request.order_id}")
            return ToolResponse(
                success=True,
                data=result,
                error=None
            )
            
        except ValueError as e:
            logger.warning(f"ValueError in list_order_items: {str(e)}")
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in list_order_items: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed"
            )

    @mcp.tool()
    def track_order(request: GetOrderRequest) -> ToolResponse:
        """
        Track real-time delivery status and location of an order. Returns the latest tracking 
        events from the tracking_event table including current status (order_placed/processing/shipped/
        in_transit/delivered/exception), physical location, and timestamp. Use this to provide 
        customers with up-to-date shipment information and delivery updates.
        
        Args:
            request: GetOrderRequest containing order_id (UUID)
            
        Returns:
            ToolResponse containing tracking events with fields: tracking_event_id, order_id, 
            status (order_placed/processing/shipped/in_transit/delivered/exception), 
            location, timestamp
        """
        logger.info(f"Executing track_order with order_id={request.order_id}")
        
        try:
            if not request or not request.order_id:
                logger.warning("Invalid order_id provided to track_order")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Invalid order ID provided"
                )
            
            # Verify order exists first
            order = get_order_by_id(request.order_id)
            if not order:
                logger.warning(f"Order not found: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found"
                )
            
            result = track_order_by_id(request.order_id)
            
            if result is None:
                result = []
            
            logger.info(f"Successfully retrieved tracking info for order {request.order_id}")
            return ToolResponse(
                success=True,
                data=result,
                error=None
            )
            
        except ValueError as e:
            logger.warning(f"ValueError in track_order: {str(e)}")
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in track_order: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed"
            )

    @mcp.tool()
    def cancel_order(request: GetOrderRequest) -> ToolResponse:
        """
        Cancel a pending order and update its status to 'cancelled'. Orders can only be cancelled 
        if they are currently in 'pending' status. Once an order has moved to processing, shipped, 
        or delivered status, it cannot be cancelled through this tool and must be handled as a 
        return or through customer support. This operation updates the orders table status field.
        
        Args:
            request: GetOrderRequest containing order_id (UUID)
            
        Returns:
            ToolResponse containing updated order data with status set to 'cancelled', 
            or error message if cancellation is not permitted
        """
        logger.info(f"Executing cancel_order with order_id={request.order_id}")
        
        try:
            if not request or not request.order_id:
                logger.warning("Invalid order_id provided to cancel_order")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Invalid order ID provided"
                )
            
            # Retrieve current order status
            order = get_order_by_id(request.order_id)
            
            if not order:
                logger.warning(f"Order not found: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order not found"
                )
            
            order_status = order.get("status", "").lower()
            
            # Check if order is already cancelled
            if order_status == "cancelled":
                logger.warning(f"Order already cancelled: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Order is already cancelled"
                )
            
            # Check if order is in pending status
            if order_status != "pending":
                logger.warning(f"Order not in pending status for cancellation: {request.order_id} (status: {order_status})")
                return ToolResponse(
                    success=False,
                    data=None,
                    error=f"Order cannot be cancelled. Current status is '{order_status}'. Only pending orders can be cancelled. Please contact support for further assistance"
                )
            
            # Perform cancellation
            result = cancel_order_by_id(request.order_id)
            
            if not result:
                logger.error(f"Failed to cancel order: {request.order_id}")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Failed to cancel order"
                )
            
            logger.info(f"Successfully cancelled order {request.order_id}")
            return ToolResponse(
                success=True,
                data=result,
                error=None
            )
            
        except ValueError as e:
            logger.warning(f"ValueError in cancel_order: {str(e)}")
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in cancel_order: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=None,
                error="Database operation failed"
            )