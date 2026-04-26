from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, get_current_user
from app.modules.auth.schemas import UserCreate, UserOut, LoginRequest, TokenOut
from app.modules.auth.service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    user = await AuthService.register_user(db, payload)
    return user


@router.post(
    "/login",
    response_model=TokenOut,
    status_code=status.HTTP_200_OK,
    summary="Login and get access token",
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    token_data = await AuthService.authenticate_user(
        db, payload.email, payload.password
    )
    return token_data


@router.get(
    "/me",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get current logged in user",
)
async def get_me(
    current_user=Depends(get_current_user),
):
    return current_user