from fastmcp import FastMCP
from server.core.logger import logger
from server.services.embedding_service import generate_embedding
from server.models.tool_output_schema import ToolResponse
from server.database.repositories.search_tool_repositories import search_documents_by_vector
from server.core.constant import MAXIMUM_RETRIEVAL_CHUNK,DEFAULT_TOP_N

def register_search_tools(mcp: FastMCP) -> None:
    """Register vector search tools with MCP server"""

    @mcp.tool()
    def search_query(
        query: str,
        top_n: int = 5,
    ) -> ToolResponse:
        """
        Search documents using vector similarity with pgvector. Converts the search query
        into a  embedding and retrieves the most semantically relevant 
        document chunks from the document table ranked by cosine similarity score.
        
        This tool enables semantic search capabilities allowing you to find documents 
        based on meaning and context rather than keyword matching. Results are ordered 
        by relevance with similarity scores ranging from 0 to 1.
        
        Args:
            query: Search query text to find relevant documents. Must be non-empty.
            top_n: Number of top results to return (1-20, default 5). Results are limited
                   to maximum 20 to ensure performance.
            
        Returns:
            ToolResponse containing list of documents with fields: document_id, original_text,
            metadata, created_at, similarity_score. Returns empty list if no relevant documents found.
        """
        logger.info(f"Executing search_query with query='{query[:50]}...' and top_n={top_n}")
        
        try:
            # ================================
            # 1. VALIDATE INPUT PARAMETERS
            # ================================
            
            if not query or not isinstance(query, str):
                logger.warning("Invalid query provided to search_query")
                return ToolResponse(
                    success=False,
                    data=[],
                    error="Query must be a non-empty string"
                )
            
            if not query.strip():
                logger.warning("Query contains only whitespace")
                return ToolResponse(
                    success=False,
                    data=[],
                    error="Query cannot be empty or contain only whitespace"
                )
            
            if not isinstance(top_n, int):
                logger.warning(f"Invalid top_n type: {type(top_n)}")
                return ToolResponse(
                    success=False,
                    data=[],
                    error="top_n must be an integer"
                )
            
            if top_n <= 0 or top_n > MAXIMUM_RETRIEVAL_CHUNK:
                logger.warning(f"top_n out of range: {top_n}")
                top_n = min(max(top_n, 1), 20)
                logger.info(f"Adjusted top_n to {top_n}")
            
            # ================================
            # 2. GENERATE QUERY EMBEDDING
            # ================================
            
            logger.debug("Generating embedding for query")
            query_embedding = generate_embedding(query)
            
            if not query_embedding:
                logger.error("Failed to generate embedding for query")
                return ToolResponse(
                    success=False,
                    data=[],
                    error="Failed to process query for search"
                )
            
            if not isinstance(query_embedding, (list, tuple)):
                logger.error(f"Invalid embedding type returned: {type(query_embedding)}")
                return ToolResponse(
                    success=False,
                    data=[],
                    error="Embedding generation failed"
                )
            
            # ================================
            # 3. PERFORM VECTOR SIMILARITY SEARCH
            # ================================
            
            logger.debug("Performing vector similarity search")
            results = search_documents_by_vector(
                embedding=query_embedding,
                top_n=top_n
            )
            
            if not results:
                logger.info(f"No documents found for query: '{query[:50]}...'")
                return ToolResponse(
                    success=True,
                    data=[],
                    error=None
                )
            
            logger.info(f"Successfully retrieved {len(results)} documents for query")
            
            # ================================
            # 4. RETURN RESULTS
            # ================================
            
            return ToolResponse(
                success=True,
                data=results,
                error=None
            )
        
        except ValueError as e:
            logger.warning(f"Validation error in search_query: {str(e)}")
            return ToolResponse(
                success=False,
                data=[],
                error=str(e)
            )
        
        except Exception as e:
            logger.error(f"Unexpected error in search_query: {str(e)}", exc_info=True)
            return ToolResponse(
                success=False,
                data=[],
                error="Vector search operation failed"
            )