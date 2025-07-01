from uuid import UUID
import uuid
import asyncio
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from session.models import Session
from session.schemas.session import SessionCreate, SessionRead
from session.tasks.session import delete_session_by_id
from config.database import async_session_maker



class SessionServices:
    async def get_session(session_id: UUID):
        async with async_session_maker() as db:
            query = select(Session).where(Session.session_id == session_id)
            result = await db.execute(query)
            session = result.scalars().first()
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            return session

    async def create(session_data: SessionCreate):
        async with async_session_maker() as db:
            session_dict = session_data.dict()
            session_dict['session_id'] = uuid.uuid4()
            new_session = Session(**session_dict)
            db.add(new_session)
            await db.commit()
            await db.refresh(new_session)
            return new_session

    
    async def delete(session_id: UUID):
        asyncio.create_task(delete_session_by_id(session_id=session_id))
        return {
            "message": f"{session_id} Delete success"
        }