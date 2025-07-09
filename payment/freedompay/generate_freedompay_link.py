import hashlib
import random
import string
import aiohttp
from config.config import FREEDOM_BACKEND_URL, FREEDOM_ENDPOINT, FREEDOM_FRONTEND_URL, FREEDOM_MERCHANT_ID, FREEDOM_SECRET_KEY


def gen_salt(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def sign_params(params: dict, script_name: str) -> str:
    """Создаёт pg_sig, MD5 от (script_name + ; + sorted params + ; + secret_key)."""
    values = [script_name] + [str(params[k]) for k in sorted(params)] + [FREEDOM_SECRET_KEY]
    return hashlib.md5(";".join(values).encode("utf-8")).hexdigest()

async def generate_freedompay_link(
        order_id: int, 
        amount: float, 
        description: str, 
        user_phone: str | None = None,
        user_email: str | None = None,
) -> str:
    salt = gen_salt()
    params = {
        "pg_order_id": str(order_id),
        "pg_merchant_id": FREEDOM_MERCHANT_ID,
        "pg_amount": f"{amount:.2f}",
        "pg_description": description,
        "pg_salt": salt,
        "pg_currency": "KGS",
        "pg_testing_mode": 1,
        "pg_check_url": f"{FREEDOM_BACKEND_URL}/orders/payment/check",
        "pg_result_url": f"{FREEDOM_BACKEND_URL}/orders/payment/result",
        "pg_success_url": f"{FREEDOM_FRONTEND_URL}/checkout/success",
        "pg_failure_url": f"{FREEDOM_FRONTEND_URL}/checkout/success",
        "pg_user_phone": user_phone,         # номер покупателя
        "pg_user_contact_email": user_email, # электронная почта
    }
    params["pg_sig"] = sign_params(params, "init_payment.php")

    async with aiohttp.ClientSession() as session:
        async with session.post(FREEDOM_ENDPOINT, data=params) as resp:
            resp.raise_for_status()
            text = await resp.text()
    # Парсим XML и извлекаем pg_redirect_url
    import xml.etree.ElementTree as ET
    root = ET.fromstring(text)
    status = root.findtext("pg_status")
    if status != "ok":
        raise RuntimeError("Ошибка FreedomPay: " + text)
    return root.findtext("pg_redirect_url")