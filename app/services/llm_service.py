from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import (
    GOOGLE_API_KEY,
    LLM_MODEL_NAME,
    TEMPERATURE,
)
from app.core.logger import logger
from app.client.client import initialize_mcp


_llm = None
_llm_with_tools = None


async def initialize_llm():
    logger.info("-----start initialization of LLM-----")
    global _llm, _llm_with_tools

    # Already initialized
    if _llm_with_tools is not None:
        return _llm_with_tools

    if not GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is missing. "
            "Please set it in your .env file."
        )

    try:
        # Get MCP tools
        tools = await initialize_mcp()

        # Create LLM
        _llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL_NAME,
            temperature=float(TEMPERATURE),
        )

        # Bind MCP tools
        _llm_with_tools = _llm.bind_tools(tools)

        logger.info(
            f"LLM initialized successfully with "
            f"{len(tools)} MCP tools"
        )

        return _llm_with_tools

    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")

        raise ConnectionError(
            f"LLM service is unavailable: {e}"
        ) from e


def get_llm():
    if _llm_with_tools is None:
        raise RuntimeError(
            "LLM is not initialized. "
            "Call initialize_llm() during application startup."
        )

    return _llm_with_tools