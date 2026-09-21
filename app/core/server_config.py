from dotenv import load_dotenv
import os
load_dotenv()

AGENT_SERVER_URL = os.getenv("AGENT_SERVER_URL")
if not AGENT_SERVER_URL:
    raise ValueError("Missing required environment variable: AGENT_SERVER_URL")

SERVERS = {
    "Ecommerce Support Server": {
        "transport": "streamable_http",
        "url": AGENT_SERVER_URL,
    },
}