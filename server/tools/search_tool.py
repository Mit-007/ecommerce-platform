from fastmcp import FastMCP
from server.database.connection import (
    get_db_connection,
    release_db_connection,
)
from server.core.logger import logger


def register_document_tools(mcp: FastMCP):
    pass