from langchain_mcp_adapters.client import MultiServerMCPClient
from app.core.server_config import SERVERS
from app.core.logger import logger


_mcp_client = None
_mcp_tools = None
_mcp_tools_dict = {}

async def initialize_mcp():
    logger.info("-----start initialization of mcp server-----")
    global _mcp_client, _mcp_tools,_mcp_tools_dict

    # Already initialized
    if _mcp_tools is not None:
        return _mcp_tools

    try:
        logger.info("Connecting to MCP server...")

        _mcp_client = MultiServerMCPClient(SERVERS)

        _mcp_tools = await _mcp_client.get_tools()

        logger.info(f"Successfully connected to MCP server and Loaded {len(_mcp_tools)} tools ")

        for tool in _mcp_tools:
            _mcp_tools_dict[tool.name] = tool

        return _mcp_tools

    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")

        raise ConnectionError(f"Failed to connect to MCP server: {e}") from e
    

def get_mcp_tools_dict():
    if _mcp_tools_dict == {}:
        raise RuntimeError(
            "MCP tools are not initialized. "
            "Call initialize_mcp() during application startup."
        )

    return _mcp_tools_dict