import os
from io import BytesIO
from PIL import Image
from fastapi import UploadFile, HTTPException
import aiofiles
import httpx
import boto3
import uuid
from fastapi import UploadFile
from botocore.client import Config
import random
import string
import asyncio

UPLOAD_DIR = "./uploaded_images/"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_FILE_SIZE_MB = 5

# Ensure upload directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

LOCALSTACK_ENDPOINT = "http://localhost:4566"
BUCKET_NAME = "product-images"
REGION = "us-east-1"

s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name=REGION,
    config=Config(signature_version="s3v4")
)

async def save_product_image(file: UploadFile) -> str:
    key = f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()

    loop = asyncio.get_running_loop()
    # Upload object to S3 (blocking call wrapped in executor)
    await loop.run_in_executor(
        None,
        lambda: s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=file.content_type,
        )
    )

    # Generate signed URL (this is a quick sync call)
    signed_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': key,
        },
        ExpiresIn=300
    )
    
    return signed_url



# Async save profile picture from UploadFile
async def save_profile_picture(profile_picture: UploadFile, existing_filename: str = None):
    file_content = await profile_picture.read()
    image = Image.open(BytesIO(file_content))

    file_extension = image.format.lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Save to BytesIO buffer
    buffer = BytesIO()
    image.save(buffer, format=image.format)
    buffer.seek(0)

    # Write to file asynchronously
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(buffer.read())

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

            # Save to buffer
            buffer = BytesIO()
            image.save(buffer, format=image.format)
            buffer.seek(0)

            # Write asynchronously
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(buffer.read())

            return unique_filename
    except Exception as e:
        print("Error saving profile picture from URL:", e)
        return None

# # OTP Generator
def generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))