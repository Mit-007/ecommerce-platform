from dotenv import load_dotenv
import os
load_dotenv()

# --------------
# error msg
# ------------
def error_msg(missing_variable):
    return f"Missing required environment variable: {missing_variable}"



# -------------
# llm config
# -------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(error_msg("GOOGLE_API_KEY"))

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
if not LLM_MODEL_NAME:
    raise ValueError(error_msg("LLM_MODEL_NAME"))

TEMPERATURE = os.getenv("TEMPERATURE","0")
if not TEMPERATURE:
    raise ValueError(error_msg("TEMPERATURE"))



# -----------
# DataBase config
# -----------
DB_HOST = os.getenv("HOST")
if not DB_HOST:
    raise ValueError(error_msg("HOST"))

DB_PORT = os.getenv("PORT")
if not DB_PORT:
    raise ValueError(error_msg("PORT"))

DB_DATABASE = os.getenv("POSTGRES_DB")
if not DB_DATABASE:
    raise ValueError(error_msg("POSTGRES_DB"))

DB_USER = os.getenv("POSTGRES_USER")
if not DB_USER:
    raise ValueError(error_msg("POSTGRES_USER"))

DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not DB_PASSWORD:
    raise ValueError(error_msg("POSTGRES_PASSWORD"))

MIN_CONNECTION_POOLING = int(os.getenv("MIN_CONNECTION_POOLING", 1))
if not MIN_CONNECTION_POOLING:
    raise ValueError(error_msg("MIN_CONNECTION_POOLING"))

MAX_CONNECTION_POOLING = int(os.getenv("MAX_CONNECTION_POOLING", 10))
if not MAX_CONNECTION_POOLING:
    raise ValueError(error_msg("MAX_CONNECTION_POOLING"))



# ------------
# JWT Token config
# ------------

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(error_msg("SECRET_KEY"))

ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise ValueError(error_msg("ALGORITHM"))

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError(error_msg("ACCESS_TOKEN_EXPIRE_MINUTES"))

REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
if not REFRESH_TOKEN_EXPIRE_DAYS:
    raise ValueError(error_msg("REFRESH_TOKEN_EXPIRE_DAYS"))