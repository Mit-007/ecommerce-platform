company = {
    "company_name" : "BuyZaar",
    "company_email": "support@buyzaar.com",
}

# set A  output_dimensionality for embedding
OUTPUT_DIMENSIONALITY = 3072


# set embedding model (gemini model)
EMBEDDING_MODEL = "gemini-embedding-2"


# set limit for maximum tool_call in single graph run
MAXIMUM_TOOL_CALLS = 10

# set chunking variables
# set always CHUNK_SIZE > CHUNK_OVERLAP
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200