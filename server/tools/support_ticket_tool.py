from fastmcp import FastMCP
from server.core.logger import logger
from server.models.tool_input_schema import CreateSupportTicket,GetSupportTicket
from server.models.tool_output_schema import ToolResponse
from server.database.repositeries import create_support_ticket_by_order_id,get_support_ticket_by_id

def register_document_tools(mcp: FastMCP):

    @mcp.tool()
    def create_support_ticket(request: CreateSupportTicket) -> ToolResponse:
        """
        Retrieve order details by order ID
        """
        try :   
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
        Retrieve order details by order ID
        """
        try :   
            result = get_support_ticket_by_id(request.support_ticket_id)
    
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

