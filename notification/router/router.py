# routers/verify.py

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from config.database import get_async_session
from notification.models.verification_codes import VerificationCode
from notification.tasks.email_utils import send_email_verification_code

from sqlalchemy import insert, select, update

router = APIRouter(prefix="/verify", tags=["Verification"])

class EmailSchema(BaseModel):
    email: str

@router.post("/send-code")
async def request_code(data: EmailSchema):
    await send_email_verification_code(data.email)
    return {"message": "Код отправлен на почту"}

class EmailCodeSchema(BaseModel):
    email: str
    code: str


@router.post("/check-code")
async def check_code(data: EmailCodeSchema, session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(
        select(VerificationCode)
        .where(VerificationCode.email == data.email)
        .order_by(VerificationCode.created_at.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()

    if not record or record.code != data.code:
        raise HTTPException(status_code=400, detail="Неверный код")

    if record.created_at < datetime.utcnow() - timedelta(minutes=10):
        raise HTTPException(status_code=400, detail="Код истёк")

    if record.is_verified:
        return {"message": "Уже подтверждено"}

    await session.execute(
        update(VerificationCode)
        .where(VerificationCode.id == record.id)
        .values(is_verified=True)
    )
    await session.commit()

    return {"message": "Почта подтверждена"}