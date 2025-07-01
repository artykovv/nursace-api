import tempfile
from fastapi import APIRouter, File, UploadFile, Depends
from typing import List
from user.auth.fastapi_users_instance import fastapi_users
from user.auth.auth import auth_backend
import pyvips
from storage.s3 import S3Client
from config.config import ACCESS_KEY, SECRET_KEY, ENDPOINT_URL, BUCKET_NAME
from user.models import User
import aiofiles
import uuid
import asyncio
import os
from PIL import Image
import io

router = APIRouter(prefix="/storage", tags=["storage"])

s3_client = S3Client(
    access_key=ACCESS_KEY,
    secret_key=SECRET_KEY,
    endpoint_url=ENDPOINT_URL,
    bucket_name=BUCKET_NAME,
)

@router.post("/upload")
async def upload_files(
    files: List[UploadFile] = File(...), 
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    uploaded_urls = []

    async def process_file(file: UploadFile):
        # Сначала читаем весь файл в temp
        temp_in = f"temp_{uuid.uuid4()}.dat"
        temp_out = f"temp_{uuid.uuid4()}.webp"
        async with aiofiles.open(temp_in, "wb") as w:
            while chunk := await file.read(1024 * 1024):
                await w.write(chunk)

        def convert():
            image = pyvips.Image.new_from_file(temp_in, access="sequential")
            image.write_to_file(temp_out, Q=80)  # Q — качество

        await asyncio.to_thread(convert)

        url = await s3_client.upload_file(temp_out, folder="nurcase")
        os.remove(temp_in)
        return url

    # Параллельная загрузка всех файлов
    uploaded_urls = await asyncio.gather(*[process_file(f) for f in files])

    return {"uploaded_urls": uploaded_urls}


@router.post("/upload/products")
async def upload_product_files(
    files: List[UploadFile] = File(...),
    current_user: User = Depends(fastapi_users.current_user(superuser=True))
):
    async def process_file(file: UploadFile):
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGBA")
        file_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_png_file, \
             tempfile.NamedTemporaryFile(delete=False, suffix=".webp") as temp_webp_file:

            # Сохраняем PNG
            image.save(temp_png_file.name, format="PNG", optimize=True)

            # Сохраняем WebP (уменьшенная копия)
            small_img = image.copy()
            small_img.thumbnail((300, 300))
            small_img.save(temp_webp_file.name, format="WEBP", quality=70)

            # Загрузка в S3
            big_url = await s3_client.upload_file(temp_png_file.name, folder="nurcase/products")
            small_url = await s3_client.upload_file(temp_webp_file.name, folder="nurcase/products")

        # Удаление после загрузки
        # os.remove(temp_png_file.name)
        # os.remove(temp_webp_file.name)

        return {
            "id": file_id,
            "big": big_url,
            "small": small_url
        }

    uploaded = await asyncio.gather(*[process_file(f) for f in files])
    return {"uploaded": uploaded}