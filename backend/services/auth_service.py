from passlib.context import CryptContext

from jose import jwt
from jose import JWTError
from datetime import datetime
from datetime import timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv(
    "SECRET_KEY"
)
print("SECRET_KEY:", SECRET_KEY)


ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str):

    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
):

    return pwd_context.verify(
        plain_password,
        hashed_password
    )


def create_access_token(data: dict):

    to_encode = data.copy()

    expire = (
        datetime.utcnow()
        + timedelta(
            minutes=
            ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

def verify_token(token: str):

    try:


        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )


        email = payload.get("sub")

        return email

    except Exception as error:

        print("JWT ERROR:", error)

        return None