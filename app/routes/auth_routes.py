from fastapi import APIRouter, HTTPException
from app.database.repositories.customer_repositories import (create_new_customer,fetch_password_by_email)
from app.utils.jwt import (
    create_access_token,
    create_refresh_token,
    refresh_access_token,
)
from app.services.hashing import verify_password
from app.model.auth_routes_schema import (
    RefreshTokenRequest,
    RegisterCustomerRequest,
    LoginCustomerRequest,
)
from app.core.logger import logger


router = APIRouter(prefix="/auth",tags=["auth"],)


@router.post("/register")
def register_new_customer(request: RegisterCustomerRequest):
    try:
        new_customer = create_new_customer(
            request.name,
            request.email,
            request.password,
        )

        return new_customer

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while creating customer: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/login")
def login_user(request: LoginCustomerRequest):
    try:
        customer_data = fetch_password_by_email(
            request.email
        )

        if customer_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Customer with email {request.email} not found.",
            )

        if not verify_password(
            request.password,
            customer_data["password"],
        ):
            raise HTTPException(
                status_code=401,
                detail="Incorrect password. Please try again.",
            )

        data = {
            "sub": str(customer_data["customer_id"])
        }

        return {
            "message": "You are logged in successfully.",
            "access_token": create_access_token(data),
            "refresh_token": create_refresh_token(data),
        }

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while logging in customer: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.post("/refresh")
def refresh_token(request: RefreshTokenRequest):
    try:
        new_access_token = refresh_access_token(
            request.refresh_token
        )

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    except HTTPException:
        raise

    except ConnectionError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail=str(e),
        )

    except Exception as e:
        logger.error(f"Error while refreshing token: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
