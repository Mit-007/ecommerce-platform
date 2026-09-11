from dotenv import load_dotenv
from pathlib import Path

import os
load_dotenv()

# --------------
# error msg
# ------------
def error_msg(missing_variable):
    return f"Missing required environment variable: {missing_variable}"


# -------------
# prompt file path
# -------------
prompt_path = os.getenv("PROMPT_FILE_PATH")
if not prompt_path:
    raise ValueError(error_msg("PROMPT_FILE_PATH"))
PROMPT_FILE_PATH = Path(prompt_path)


# -------------
# llm config
# -------------
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(error_msg("GOOGLE_API_KEY"))

LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
if not LLM_MODEL_NAME:
    raise ValueError(error_msg("LLM_MODEL_NAME"))

TEMPERATURE = float(os.getenv("TEMPERATURE", "0.0"))
if not (0 <= TEMPERATURE <= 2.0):
    raise ValueError("TEMPERATURE must be between 0 and 2.0")



# -----------
# DataBase config
# -----------
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


# ------------
# JWT Token config
# ------------

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError(error_msg("SECRET_KEY"))

ALGORITHM = os.getenv("ALGORITHM")
if not ALGORITHM:
    raise ValueError(error_msg("ALGORITHM"))


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be > 0")


REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
if REFRESH_TOKEN_EXPIRE_DAYS <= 0:
    raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be > 0")
