from dotenv import load_dotenv
import os
load_dotenv()

def error_msg(missing_variable):
    return f"Missing required environment variable: {missing_variable}"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(error_msg("GOOGLE_API_KEY"))

DB_HOST = os.getenv("HOST")
if not DB_HOST:
    raise ValueError(error_msg("HOST"))

DB_PORT = int(os.getenv("PORT", "5432"))
if not DB_PORT or DB_PORT <= 0:
    raise ValueError("Database port must be a positive integer.")

DB_DATABASE = os.getenv("POSTGRES_DB")
if not DB_DATABASE:
    raise ValueError(error_msg("POSTGRES_DB"))

DB_USER = os.getenv("POSTGRES_USER")
if not DB_USER:
    raise ValueError(error_msg("POSTGRES_USER"))

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not DB_PASSWORD:
    raise ValueError(error_msg("POSTGRES_PASSWORD"))

MIN_CONNECTION_POOLING = int(os.getenv("MIN_CONNECTION_POOLING", "1"))
if MIN_CONNECTION_POOLING <= 0:
    raise ValueError("MIN_CONNECTION_POOLING must be > 0")

MAX_CONNECTION_POOLING = int(os.getenv("MAX_CONNECTION_POOLING", "10"))
if MAX_CONNECTION_POOLING <= MIN_CONNECTION_POOLING:
    raise ValueError("MAX_CONNECTION_POOLING must be > MIN_CONNECTION_POOLING")


SERVER_HOST = os.getenv("SERVER_HOST")
if not SERVER_HOST:
    raise ValueError(error_msg("SERVER_HOST"))

SERVER_PORT = int(os.getenv("SERVER_PORT", "3000"))
if not SERVER_PORT or SERVER_PORT <= 0:
    raise ValueError("MCP port must be a positive integer.")
