import contextlib
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from app.core.server_config import SERVERS
from app.core.logger import logger

_mcp_client = None
_mcp_tools_dict = {}
# FIX: Use an exit stack to keep all MCP sessions alive globally
_exit_stack = contextlib.AsyncExitStack() 

async def initialize_mcp():
    logger.info("-----start initialization of mcp server-----")
    global _mcp_client, _mcp_tools_dict

    # Already initialized
    if _mcp_tools_dict:
        return list(_mcp_tools_dict.values())

    try:
        logger.info("Connecting to MCP server...")
        _mcp_client = MultiServerMCPClient(SERVERS)
        
        all_tools = []
        
        # FIX: Open a persistent session for EVERY server in your config
        for server_name in SERVERS.keys():
            # Enter the context manager and keep it open in the background
            session = await _exit_stack.enter_async_context(
                _mcp_client.session(server_name)
            )
            
            # Load tools using the persistent session
            server_tools = await load_mcp_tools(session)
            all_tools.extend(server_tools)

        logger.info(f"Successfully connected to MCP server and Loaded {len(all_tools)} tools")

        for tool in all_tools:
            _mcp_tools_dict[tool.name] = tool

        return all_tools

    except Exception as e:
        logger.error(f"Failed to connect to MCP server: {e}")
        raise ConnectionError(f"Failed to connect to MCP server: {e}") from e
    

def get_mcp_tools_dict():
    if not _mcp_tools_dict:
        raise RuntimeError(
            "MCP tools are not initialized. "
            "Call initialize_mcp() during application startup."
        )
    return _mcp_tools_dict

# Optional but recommended: Call this when your app shuts down
async def close_mcp():
    await _exit_stack.aclose()