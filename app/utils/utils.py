import os
import uuid
import random
import string
import re
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException
import aiofiles
import httpx

UPLOAD_DIR = "./uploaded_images/"
PRODUCT_UPLOAD_DIR = "uploads/products"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(PRODUCT_UPLOAD_DIR, exist_ok=True)


# Async save profile picture from UploadFile
async def save_profile_picture(profile_picture: UploadFile, existing_filename: str = None):
    file_content = await profile_picture.read()
    image = Image.open(BytesIO(file_content))

    file_extension = image.format.lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save image using Pillow and aiofiles
    async with aiofiles.open(file_path, "wb") as f:
        image.save(f, format=image.format)

    return unique_filename


# Async save profile picture from URL
async def save_profile_picture_from_url(profile_picture_url: str, existing_filename: str = None):
    if not profile_picture_url:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(profile_picture_url)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            file_extension = image.format.lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            async with aiofiles.open(file_path, "wb") as f:
                image.save(f, format=image.format)

            return unique_filename
    except Exception as e:
        print("Error saving profile picture from URL:", e)
        return None


# OTP Generator
def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))


# Async save product image with validation
async def save_product_image(image: UploadFile) -> str:
    ext = image.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only JPG/PNG files are allowed")

    content = await image.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB")

    image.file.seek(0)
    filename = f"{uuid.uuid4()}.{ext}"
    file_path = os.path.join(PRODUCT_UPLOAD_DIR, filename)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)

    return f"/{PRODUCT_UPLOAD_DIR}/{filename}"
