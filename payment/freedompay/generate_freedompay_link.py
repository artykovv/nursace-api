import hashlib
import random
import string
import aiohttp

MERCHANT_ID = "560549"   # получите у FreedomPay sandbox
SECRET_KEY = "enHj3DskKDcVLoaj"     # тестовый ключ
ENDPOINT = "https://api.freedompay.kg/init_payment.php"

def gen_salt(length: int = 16) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))

def sign_params(params: dict, script_name: str) -> str:
    """Создаёт pg_sig, MD5 от (script_name + ; + sorted params + ; + secret_key)."""
    values = [script_name] + [str(params[k]) for k in sorted(params)] + [SECRET_KEY]
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
        "pg_merchant_id": MERCHANT_ID,
        "pg_amount": f"{amount:.2f}",
        "pg_description": description,
        "pg_salt": salt,
        "pg_currency": "KGS",
        "pg_testing_mode": 1,             # тестовый режим  [oai_citation:0‡freedompay.kg](https://freedompay.kg/docs-en/merchant-api/pay?utm_source=chatgpt.com)
        "pg_check_url": "https://http://127.0.0.1:8000/orders/payment/check",
        "pg_result_url": "https://http://127.0.0.1:8000/orders/payment/result",
        "pg_success_url": "https://http://127.0.0.1:8001/orders/success",
        "pg_failure_url": "https://http://127.0.0.1:8001/orders/failure",
        "pg_user_phone": user_phone,         # номер покупателя
        "pg_user_contact_email": user_email, # электронная почта
    }
    params["pg_sig"] = sign_params(params, "init_payment.php")

    async with aiohttp.ClientSession() as session:
        async with session.post(ENDPOINT, data=params) as resp:
            resp.raise_for_status()
            text = await resp.text()
    # Парсим XML и извлекаем pg_redirect_url
    import xml.etree.ElementTree as ET
    root = ET.fromstring(text)
    status = root.findtext("pg_status")
    if status != "ok":
        raise RuntimeError("Ошибка FreedomPay: " + text)
    return root.findtext("pg_redirect_url")