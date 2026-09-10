from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
from app.core.logger import logger

hasher = PasswordHasher()

def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    if not password or not isinstance(password, str):
        raise ValueError("Password must be a non-empty string")
    
    try:
        return hasher.hash(password)
    except Exception as e:
        logger.error(f"Error hashing password: {e}")
        raise RuntimeError("Failed to hash password") from e

def verify_password(user_password: str, original_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        if not user_password or not original_password:
            logger.debug("Password verification failed: empty password")
            return False
        
        hasher.verify(original_password, user_password)  # Note: correct order
        return True
    
    except VerifyMismatchError:
        logger.debug("Password verification failed: password mismatch")
        return False
    
    except InvalidHash:
        logger.warning("Password verification failed: invalid hash format")
        return False
    
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {e}")
        return False