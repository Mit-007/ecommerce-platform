from datetime import datetime, timedelta, timezone
from jose import jwt ,JWTError
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES,REFRESH_TOKEN_EXPIRE_DAYS,SECRET_KEY,ALGORITHM

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

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload.update({
        "exp": expire,
        "type": "access"
    })

    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token


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

    payload = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        days=REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload.update({
        "exp": expire,
        "type": "refresh"
    })

    refresh_token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return refresh_token

# ==============================
# verify the access token 
# ==============================
def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "access":
            return None

        return payload

    except JWTError:
        return None

# ==============================
# Create Access Token from using Refresh Token
# ==============================
def refresh_access_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        if payload.get("type") != "refresh":
            return None

        customer_id = payload.get("sub")

        if not customer_id:
            return None

        new_access_token = create_access_token({
            "sub": customer_id
        })

        return new_access_token

    except JWTError:
        return None


# print(verify_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTVmNTUzMC00NmQ2LTRmYTctODMzYi1hY2NkZDMxMTA3YmMiLCJleHAiOjE3ODg1MjkyNDUsInR5cGUiOiJhY2Nlc3MifQ.ZEm75aBL29xeyLQFTdp0BeSIuU0mXelZ_D-DPCosEPM"))
# print(refresh_access_token("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYTVmNTUzMC00NmQ2LTRmYTctODMzYi1hY2NkZDMxMTA3YmMiLCJleHAiOjE3ODkxMjg4MzcsInR5cGUiOiJyZWZyZXNoIn0.xeL-SRu4-wNcob5LHVx9BH-W8vZnwr28R4ShtSXgq1M"))