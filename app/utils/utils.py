import os
from io import BytesIO
from PIL import Image
from fastapi import UploadFile
import aiofiles
import httpx
import uuid
import random
import string

UPLOAD_DIR = "./uploaded_images/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Async save profile picture (from UploadFile)
async def save_profile_picture(
    profile_picture: UploadFile, existing_filename: str = None
):
    file_content = await profile_picture.read()
    image = Image.open(BytesIO(file_content))

    file_extension = image.format.lower()
    unique_filename = (
        f"{uuid.uuid4()}.{file_extension}"
        if existing_filename is None
        else existing_filename
    )
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    buffer = BytesIO()
    image.save(buffer, format=image.format)
    buffer.seek(0)

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(buffer.read())

    return unique_filename


# Async save profile picture from a URL
async def save_profile_picture_from_url(
    profile_picture_url: str, existing_filename: str = None
):
    if not profile_picture_url:
        return None

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(profile_picture_url)
            response.raise_for_status()

            image = Image.open(BytesIO(response.content))
            file_extension = image.format.lower()
            unique_filename = (
                f"{uuid.uuid4()}.{file_extension}"
                if existing_filename is None
                else existing_filename
            )
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            buffer = BytesIO()
            image.save(buffer, format=image.format)
            buffer.seek(0)

            async with aiofiles.open(file_path, "wb") as f:
                await f.write(buffer.read())

            return unique_filename
    except Exception as e:
        print("Error saving profile picture from URL:", e)
        return None


# OTP Generator
def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))
