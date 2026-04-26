from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(
        plain.encode("utf-8"),
        hashed.encode("utf-8")
    )


def create_access_token(data: dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token")