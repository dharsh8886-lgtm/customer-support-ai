from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "TechNovaSecretKey123"
ALGORITHM = "HS256"


def create_access_token(email):

    expire = datetime.utcnow() + timedelta(hours=24)

    payload = {
        "sub": email,
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def verify_access_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload["sub"]

    except Exception:
        return None
