# services/email_verification.py

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from notification.models import VerificationCode
from config.database import async_session_maker

import random
import aiosmtplib
from email.message import EmailMessage
from datetime import datetime

from config.config import SMTP_USER, SMTP_PASS, SMTP_HOST, SMTP_PORT


def generate_code() -> str:
    return f"{random.randint(1000, 9999)}"


async def send_email_verification_code(email: str):
    print(f"[DEBUG] Отправка кода подтверждения для email = {email}")
    
    # Проверка времени последней отправки
    async with async_session_maker() as session:
        result = await session.execute(
            select(VerificationCode)
            .where(VerificationCode.email == email)
            .order_by(VerificationCode.created_at.desc())
            .limit(1)
        )
        last_code = result.scalar_one_or_none()
        if last_code:
            seconds_passed = (datetime.utcnow() - last_code.created_at).total_seconds()
            if seconds_passed < 60:
                raise HTTPException(status_code=429, detail=f"Пожалуйста, подождите {int(60 - seconds_passed)} секунд перед повторной отправкой")

    # Генерация и отправка (как было раньше)
    code = generate_code()
    html_body = f"""
    <html>
    <body>
        <h2>Подтверждение почты</h2>
        <p>Ваш код подтверждения: <strong style="font-size: 24px;">{code}</strong></p>
        <p>Введите этот код в приложении.</p>
        <p>С уважением,<br>Команда <strong>Style Shoes</strong></p>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg["From"] = f"Style Shoes <{SMTP_USER}>"
    msg["To"] = email
    msg["Subject"] = "Код подтверждения"

    msg.set_content(f"Ваш код подтверждения: {code}")
    msg.add_alternative(html_body, subtype="html")

    try:
        smtp = aiosmtplib.SMTP(hostname=SMTP_HOST, port=SMTP_PORT, start_tls=True)
        await smtp.connect()
        await smtp.login(SMTP_USER, SMTP_PASS)
        await smtp.send_message(msg)
        await smtp.quit()
        print(f"[DEBUG] Код отправлен на {email}")
    except Exception as e:
        print(f"[ERROR] Ошибка при отправке письма: {e}")
        raise

    # Сохраняем код
    async with async_session_maker() as session:
        stmt = insert(VerificationCode).values(email=email, code=code)
        await session.execute(stmt)
        await session.commit()
        print(f"[DEBUG] Код {code} сохранён в БД для {email}")