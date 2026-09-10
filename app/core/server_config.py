from dotenv import load_dotenv
import os
load_dotenv()

SERVERS = {
    "Ecommerce Support Server": {
        "transport": "streamable_http",
        "url": os.getenv("AGENT_SERVER_URL")
    },
}