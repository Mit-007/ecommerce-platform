from fastmcp import FastMCP
from server.core.logger import logger
from server.models.tool_input_schema import CreateSupportTicket,GetSupportTicket
from server.models.tool_output_schema import ToolResponse
from server.database.repositories.support_ticket_tool_repositories import create_support_ticket_by_order_id,get_support_ticket_by_id

def register_support_ticket_tools(mcp: FastMCP):

    @mcp.tool()
    def create_support_ticket(request: CreateSupportTicket) -> ToolResponse:
        """
        Create a new support ticket for an order. Captures customer issues 
        and associates them with the order and conversation for tracking.
        """
        logger.info("Tool_call : create_support_ticket")
        try:   
            result = create_support_ticket_by_order_id(request.order_id,request.summary,request.conversation_id)

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
    def get_support_ticket(request: GetSupportTicket) -> ToolResponse:
        """
        Retrieve details of a specific support ticket by ticket ID.
        """
        logger.info("Tool_call : get_support_ticket")
        try:   
            result = get_support_ticket_by_id(request.support_ticket_id)
            
            return ToolResponse(
                success = True,
                data = result,
                error = None
            )
    
        except Exception as e:
            logger.exception(f"Unexpected error in get_support_ticket:{e}")
            return ToolResponse(
                success = False,
                data = None ,
                error = str(e)   
            )

