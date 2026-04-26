from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from app.modules.auth.model import User
from app.modules.auth.schemas import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings


class AuthService:

    @staticmethod
    async def register_user(db: AsyncSession, payload: UserCreate) -> User:
        # check if email already exists
        result = await db.execute(
            select(User).where(User.email == payload.email)
        )
        existing = result.scalar_one_or_none()

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A user with this email already exists",
            )

        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
            is_active=True,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, email: str, password: str
    ) -> dict:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account is inactive",
            )

        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }