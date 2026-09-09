from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.connection import init_db_pool, close_db_pool
from app.routes import support_route, auth_routes, order_routes,customer_routes , invoice_routes ,tracking_routes ,converstion_routes
from app.services.llm_service import initialize_llm
from app.services.prompt_templete import initialize_prompt_templates
from app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):

    try:
        # =========================
        # STARTUP
        # =========================

        logger.info("Application startup started.")

        init_db_pool()
        logger.info("Database pool initialized.")

        initialize_prompt_templates()
        logger.info("Prompt templates initialized.")

        await initialize_llm()
        logger.info("LLM initialized.")

        logger.info("Application startup completed.")

        yield

    except Exception as e:
        logger.exception(f"Application startup failed: {e}")
        raise

    finally:
        # =========================
        # SHUTDOWN
        # =========================

        logger.info("Application shutdown started.")

        close_db_pool()

        logger.info("Application shutdown completed.")

app = FastAPI(lifespan=lifespan)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
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
app.include_router(converstion_routes.router)