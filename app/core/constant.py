from datetime import datetime
from zoneinfo import ZoneInfo

current_datetime = datetime.now(ZoneInfo("Asia/Kolkata"))

dateTime = {
    "current_date" : current_datetime.strftime("%Y-%m-%d"),
    "current_time" : current_datetime.strftime("%H:%M:%S"),
    "current_weekday" : current_datetime.strftime("%A"),
}

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