from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import init_db_pool, close_db_pool
from app.routes import (
    conversation_routes,
    support_route, 
    auth_routes, 
    order_routes,
    customer_routes , 
    invoice_routes ,
    tracking_routes ,
    document_routes,
)
from app.services.llm_service import initialize_llm
from app.services.prompt_template import initialize_prompt_templates
from app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        # =========================
        # STARTUP
        # =========================
        init_db_pool()

        initialize_prompt_templates()

        await initialize_llm()

        logger.info("Application startup completed.")

        yield

    except ValueError as e:
        logger.error(f"Configuration error during startup: {e}")
        raise   
    except ConnectionError as e:
        logger.error(f"Database connection error during startup: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during application startup: {e}", exc_info=True)
        raise RuntimeError(f"Failed to start application: {e}") from e

    finally:
        # =========================
        # SHUTDOWN
        # =========================

        logger.info("Application shutdown started.")

        close_db_pool()

        logger.info("Application shutdown completed.")

app = FastAPI(lifespan=lifespan)

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(support_route.router)
app.include_router(auth_routes.router)
app.include_router(customer_routes.router)
app.include_router(invoice_routes.router)
app.include_router(order_routes.router)
app.include_router(tracking_routes.router)
app.include_router(conversation_routes.router)
app.include_router(document_routes.router)