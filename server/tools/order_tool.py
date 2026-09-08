from fastmcp import FastMCP
from server.core.logger import logger
from server.models.tool_input_schema import GetOrderRequest
from server.models.tool_output_schema import ToolResponse
from server.database.repositories.order_tool_repositories import get_order_by_id,track_order_by_id,cancel_order_by_id,list_order_items_by_order_id


def register_document_tools(mcp: FastMCP):

    @mcp.tool()
    def get_order(request: GetOrderRequest) -> ToolResponse:
        """
        Retrieve order details by order ID
        
        Args:
            request: GetOrderRequest with order_id
            
        Returns:
            ToolResponse with order data or error
        """
        logger.info("Tool_call : get_order")
        try :   
            result = get_order_by_id(request.order_id)

            logger.info(" ---> order_detils:")
            logger.info(result)

            return ToolResponse(
                success = True,
                data = result,
                error = None
            )

        except Exception as e:
            logger.exception(e)
            return ToolResponse(
                success = False,
                data = None ,
                error = str(e)   
            )

    @mcp.tool()
    def list_order_items(request: GetOrderRequest) -> ToolResponse:
        """
        List all items belonging to an order by order ID.
        """
        logger.info("Tool_call : list_order_items")

        try:
            result = list_order_items_by_order_id(request.order_id)

            logger.info(" ---> Order_items:")
            logger.info(result)

            return ToolResponse(
                success=True,
                data=result,
                error=None,
            )

        except Exception as e:
            logger.exception(e)

            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        
    @mcp.tool()
    def track_order(request: GetOrderRequest) -> ToolResponse:
        """
        Track a order delivery by order ID
        """
        logger.info("Tool_call : track_order")
        try :   
            result = track_order_by_id(request.order_id)

            logger.info(" ---> Tracking_detils:")
            logger.info(result)

            return ToolResponse(
                success = True,
                data = result,
                error = None
            )
    
        except Exception as e:
            logger.exception(e)
            return ToolResponse(
                success = False,
                data = None ,
                error = str(e)   
            )

    @mcp.tool
    def cancle_order(request : GetOrderRequest) -> ToolResponse:
        """
        take order id , check order status if it is a "Pending" then cancle permited otherwise oreder not cancle.
        """
        logger.info("Tool_call : cancle_order")
        try:
            result = get_order_by_id(request.order_id)

            if result['status'] == "cancelled":
                raise ValueError("order are already cancelled.")

            if result['status'] != "pending":
                raise ValueError("order is not in pending status that why not ,cancle ie , contact to human for further prodess")

                
            result = cancel_order_by_id(request.order_id)

            logger.info(" ---> order cancle sucessfully,:")
            logger.info(result)

            return ToolResponse(
                success = True,
                data = result,
                error = None
            )
            
        except Exception as e:
            logger.exception(e)
            return ToolResponse(
                success = False,
                data = None ,
                error = str(e)   
            )