from contextlib import asynccontextmanager
from fastmcp import FastMCP
from server.database.connection import (
    init_db_pool,
    close_db_pool,
)
from server.tools import (
    document_tool as DT,
    order_tool as OT,
    search_tool as ST,
    support_ticket_tool as TT
)
from server.core.logger import logger

@asynccontextmanager
async def lifespan(server: FastMCP):

    try:
        logger.info("Initializing database connection pool...")
        init_db_pool()
        logger.info("Database connection pool initialized")
        
    except Exception as e:
        logger.exception(f"Failed to initialize database pool: {e}")
        raise

    try:
        yield

    finally:
        # Shutdown
        close_db_pool()


mcp = FastMCP(
    "Ecommerce Support Server",
    lifespan=lifespan
)


# Register MCP tools
DT.register_document_tools(mcp)
OT.register_document_tools(mcp)
ST.register_search_tools(mcp)
TT.register_document_tools(mcp)


if __name__ == "__main__":

    try:
        mcp.run(
            transport="http",
            host="0.0.0.0",
            port=3001,
        )

    except Exception:
        raise