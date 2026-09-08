from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils.jwt import verify_access_token

security = HTTPBearer()

# ==============================
# Get Current Customer from Token
# ==============================
def get_current_customer(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """
    Dependency function to verify access token and extract customer_id.
    
    Used with Depends() to protect routes.
    """
    
    token = credentials.credentials
    
    # Verify the token
    payload = verify_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract customer_id from token payload
    customer_id = payload.get("sub")
    
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return customer_id