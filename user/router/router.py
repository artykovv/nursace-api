from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from user.auth.fastapi_users_instance import fastapi_users
from user.auth.auth import auth_backend
from user.models import User
from user.schemas.user import UserRead, UserCreate, UserUpdate
from user.services.user import UserService
from config.database import get_async_session
from uuid import UUID

router = APIRouter(tags=["user"])


router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt"
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth"
)

@router.get("/auth/validate-token")
async def validate_token(current_user: User = Depends(fastapi_users.current_user())):
    return {
        "message": "Token is valid", 
        # "user_id": current_user
    }

@router.get("/auth/admin-token")
async def validate_token(current_user: User = Depends(fastapi_users.current_user(superuser=True))):
    return {
        "message": "Token is valid"
    }



@router.get("/user/me", response_model=UserRead)
async def read_user_me(
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user())
):
    if current_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return current_user

@router.get("/user/{user_id}", response_model=UserRead)
async def read_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    db_user = await UserService.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.get("/users/", response_model=list[UserRead])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    users = await UserService.get_all_users(db, skip=skip, limit=limit)
    return users

@router.patch("/user/{user_id}", response_model=UserRead)
async def update_user(
    user_id: UUID,
    user: UserUpdate,
    current_user: User = Depends(fastapi_users.current_user(superuser=True)),
    db: AsyncSession = Depends(get_async_session),
):
    db_user = await UserService.get_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    updated_user = await UserService.update_user(db, user_id, user)
    return updated_user

@router.delete("/user/{user_id}")
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    db_user = await UserService.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}