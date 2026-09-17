from jose import JWTError, ExpiredSignatureError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID
from app.core.config import (
    SECRET_KEY,
    ALGORITHM,
)
from app.core.logger import logger

# HTTP Bearer security scheme for extracting Bearer token from headers
security_scheme = HTTPBearer(auto_error=False)


# ==============================
# Decode and Verify Generic JWT Token
# ==============================
def decode_jwt_token(token: str) -> dict:
    """
    Decode a JWT token with full signature and expiration verification.
    Raises:
        HTTPException: If token is expired or invalid.
    """
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload

    except ExpiredSignatureError:
        logger.warning("JWT Token has expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        logger.warning(f"Invalid JWT Token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.exception(f"Unexpected error while decoding JWT: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed.",
            headers={"WWW-Authenticate": "Bearer"},
        )

# ==============================
# FastAPI Auth Dependency
# ==============================
def get_current_customer(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> dict:
    """
    FastAPI dependency to extract and validate the JWT Bearer token
    from the Authorization HTTP header.

    Returns:
        dict: Token payload including 'customer_id' and 'sub'.
    Raises:
        HTTPException 401: If header is missing, token is expired or invalid.
    """
    if credentials is None or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication scheme. 'Bearer' token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_jwt_token(credentials.credentials)

    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type. Access token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    customer_id = payload.get("sub")
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token subject ('sub') claim is missing.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Validate that customer_id is a valid UUID format
        UUID(customer_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid customer ID in token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Return standard payload with customer_id
    return {
        "customer_id": customer_id,
        "sub": customer_id,
        "token_type": token_type,
        "exp": payload.get("exp"),
        "iat": payload.get("iat"),
        "jti": payload.get("jti"),
    }


def get_current_customer_id(
    current_customer: dict = Depends(get_current_customer),
) -> UUID:
    """
    FastAPI dependency that returns the authenticated customer's UUID.
    """
    return UUID(current_customer["customer_id"])