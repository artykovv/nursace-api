from uuid import UUID
from fastapi import APIRouter

from session.services.session import SessionServices
from session.schemas.session import SessionRead, SessionCreate

router = APIRouter(prefix="/session", tags=["session"])

@router.post("/")
async def create_new_session(
    create: SessionCreate
):
    session = await SessionServices.create(session_data=create)
    return session

@router.get("/{session_id}", response_model=SessionRead)
async def get_session_by_id(session_id: UUID):
    session = await SessionServices.get_session(session_id=session_id)
    return session