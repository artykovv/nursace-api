# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi_users.password import PasswordHelper
from user.models import User, Branch
from user.schemas.user import UserCreate, UserUpdate
from uuid import UUID

class UserService:
    @staticmethod
    async def get_user(db: AsyncSession, user_id: UUID):
        result = await db.execute(
            select(User)
            .options(selectinload(User.branches))
            .filter(User.id == user_id)
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_users(db: AsyncSession, skip: int = 0, limit: int = 100):
        result = await db.execute(
            select(User)
            .options(selectinload(User.branches))
            .offset(skip)
            .limit(limit)
            .where(User.is_superuser != True)
        )
        return result.scalars().all()

    @staticmethod
    async def update_user(db: AsyncSession, user_id: UUID, user_data: UserUpdate):
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "password" and value:
                password_helper = PasswordHelper()
                value = password_helper.hash(value)
            elif key == "branch_ids" and value is not None:
                branches = await db.execute(
                    select(Branch).where(Branch.id.in_(value))
                )
                db_user.branches = branches.scalars().all()
            else:
                setattr(db_user, key, value)
        
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def delete_user(db: AsyncSession, user_id: UUID):
        db_user = await UserService.get_user(db, user_id)
        if not db_user:
            return None
        
        await db.delete(db_user)
        await db.commit()
        return db_user