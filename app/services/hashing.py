from argon2 import PasswordHasher

hasher = PasswordHasher()

def hash_password(password):
    return hasher.hash(password)

def verify_password(user_password,original_password):
    try:
        hasher.verify(original_password,user_password)
        return True
    except:
        print('Wrong password :')
        return False