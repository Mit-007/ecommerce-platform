import asyncio
from fastmcp import FastMCP
from server.core.logger import logger
from server.services.embedding_service import generate_embedding
from server.models.tool_output_schema import ToolResponse
from server.models.tool_input_schema import searchQuery
from server.database.repositories.search_tool_repositories import (
    search_documents_by_vector,
)


def register_search_tools(mcp: FastMCP) -> None:
    """Register vector search tools with MCP server"""

    @mcp.tool()
    async def search_query(request: searchQuery) -> ToolResponse:
        """
        Search documents using vector similarity with pgvector.
        Converts the search query into an embedding and retrieves
        the most semantically relevant document chunks.
        """

        logger.info("Executing search_query...")

        try:
            # Generate query embedding in a worker thread
            query_embedding = await asyncio.to_thread(
                generate_embedding,
                request.query,
            )

            if not query_embedding:
                logger.error(
                    "Failed to generate embedding for query"
                )

                return ToolResponse(
                    success=False,
                    data=None,
                    error="Failed to process query for search",
                )

            # Perform vector similarity search in a worker thread
            results = await asyncio.to_thread(
                search_documents_by_vector,
                embedding=query_embedding,
                top_n=request.top_n,
            )

            logger.info(
                f"Successfully retrieved {len(results)} "
                f"documents for query"
            )

            return ToolResponse(
                success=True,
                data=results,
                error=None,
            )

        except ValueError as e:
            logger.warning(
                f"Validation error in search_query: {str(e)}"
            )

            return ToolResponse(
                success=False,
                data=None,
                error=str(e),
            )

        except Exception as e:
            logger.error(
                f"Unexpected error in search_query: {str(e)}",
                exc_info=True,
            )

            return ToolResponse(
                success=False,
                data=None,
                error="Vector search operation failed",
            )