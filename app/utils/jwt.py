from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
    SECRET_KEY,
    ALGORITHM,
)
from app.core.logger import logger


# ==============================
# Create Access Token
# ==============================
def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    Access token:
    - Short-lived
    - Used for accessing protected APIs
    """

    try:
        payload = data.copy()

        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload.update({
            "exp": expire,
            "type": "access",
        })

        access_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return access_token

    except Exception as e:
        logger.exception("Failed to create access token.")
        raise RuntimeError(
            f"Failed to create access token: {e}"
        ) from e


# ==============================
# Create Refresh Token
# ==============================
def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token.
    Refresh token:
    - Long-lived
    - Used to generate a new access token
    """

    try:
        payload = data.copy()

        expire = datetime.now(timezone.utc) + timedelta(
            days=REFRESH_TOKEN_EXPIRE_DAYS
        )

        payload.update({
            "exp": expire,
            "type": "refresh",
        })

        refresh_token = jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM,
        )

        return refresh_token

    except Exception as e:
        logger.exception("Failed to create refresh token.")
        raise RuntimeError(
            f"Failed to create refresh token: {e}"
        ) from e


# ==============================
# Verify Access Token
# ==============================
def verify_access_token(token: str) -> dict | None:
    """
    Verify and decode an access token.
    Returns:
        dict: JWT payload if valid.
        None: If token is invalid, expired, or not an access token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            logger.warning("Invalid token type for access token.")
            return None

        if not payload.get("sub"):
            logger.warning("Access token does not contain 'sub'.")
            return None

        return payload

    except JWTError:
        logger.warning("Invalid or expired access token.")
        return None

    except Exception as e:
        logger.exception(
            f"Unexpected error while verifying access token: {e}"
        )
        return None


# ==============================
# Create Access Token
# Using Refresh Token
# ==============================
def refresh_access_token(refresh_token: str) -> str | None:
    """
    Verify a refresh token and generate a new access token.

    Returns:
        str: New access token if refresh token is valid.
        None: If refresh token is invalid or expired.
    """

    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "refresh":
            logger.warning("Invalid token type for refresh token.")
            return None

        customer_id = payload.get("sub")

        if not customer_id:
            logger.warning("Refresh token does not contain 'sub'.")
            return None

        new_access_token = create_access_token({
            "sub": customer_id,
        })

        return new_access_token

    except JWTError:
        logger.warning("Invalid or expired refresh token.")
        return None

    except Exception as e:
        logger.exception(
            f"Unexpected error while refreshing access token: {e}"
        )
        return None