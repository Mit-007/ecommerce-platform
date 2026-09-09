from dotenv import load_dotenv
import os
load_dotenv()

def error_msg(missing_variable):
    return f"Missing required environment variable: {missing_variable}"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(error_msg(GOOGLE_API_KEY))

DB_HOST = os.getenv("HOST")
if not DB_HOST:
    raise ValueError(error_msg(DB_HOST))

DB_PORT = os.getenv("PORT")
if not DB_PORT:
    raise ValueError(error_msg(DB_PORT))

DB_DATABASE = os.getenv("POSTGRES_DB")
if not DB_DATABASE:
    raise ValueError(error_msg(DB_DATABASE))

DB_USER = os.getenv("POSTGRES_USER")
if not DB_USER:
    raise ValueError(error_msg(DB_USER))

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not DB_PASSWORD:
    raise ValueError(error_msg(DB_PASSWORD))

MIN_CONNECTION_POOLING = int(os.getenv("MIN_CONNECTION_POOLING", 1))
if not MIN_CONNECTION_POOLING:
    raise ValueError(error_msg(MIN_CONNECTION_POOLING))

MAX_CONNECTION_POOLING = int(os.getenv("MAX_CONNECTION_POOLING", 10))
if not MAX_CONNECTION_POOLING:
    raise ValueError(error_msg(MAX_CONNECTION_POOLING))