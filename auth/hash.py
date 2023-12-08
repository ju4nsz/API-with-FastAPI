from passlib.context import CryptContext
from bcrypt import hashpw, gensalt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    salt = gensalt()
    hashed_password = hashpw(password.encode("utf-8"), salt)
    return hashed_password

def verify_password(plane_password, hashed_password):
    return pwd_context.verify(plane_password, hashed_password)