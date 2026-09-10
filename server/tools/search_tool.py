from fastmcp import FastMCP
from server.core.logger import logger
from server.services.embedding_service import generate_embedding
from server.models.tool_output_schema import ToolResponse
from server.models.tool_input_schema import searchQuery
from server.database.repositories.search_tool_repositories import search_documents_by_vector

def register_search_tools(mcp: FastMCP) -> None:
    """Register vector search tools with MCP server"""

    @mcp.tool()
    def search_query(request:searchQuery) -> ToolResponse:
        """
        Search documents using vector similarity with pgvector. Converts the search query
        into an embedding and retrieves the most semantically relevant 
        document chunks from the document table ranked by cosine similarity score.
        
        This tool enables semantic search capabilities allowing you to find documents 
        based on meaning and context rather than keyword matching. Results are ordered 
        by relevance with similarity scores.
        """
        logger.info(f"Executing search_query...")
        
        try:
            query_embedding = generate_embedding(request.query)
            
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return ToolResponse(
                    success=False,
                    data=None,
                    error="Failed to process query for search"
                )
            

            #  PERFORM VECTOR SIMILARITY SEARCH
            results = search_documents_by_vector(
                embedding=query_embedding,
                top_n=request.top_n
            )
            
            logger.info(f"Successfully retrieved {len(results)} documents for query")
            
            return ToolResponse(
                success=True,
                data=results,
                error=None
            )
        
        except ValueError as e:
            logger.warning(f"Validation error in search_query: {str(e)}")
            return ToolResponse(
                success=False,
                data=None,
                error=str(e)
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in search_query: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=None,
                error="Vector search operation failed"
            )