from argon2 import PasswordHasher
from app.core.logger import logger

hasher = PasswordHasher()

def hash_password(password):
    return hasher.hash(password)

def verify_password(user_password,original_password):
    try:
        hasher.verify(original_password,user_password)
        return True
    except:
        logger.info('Wrong password :')
        return False