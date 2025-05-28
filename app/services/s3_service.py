from fastapi import UploadFile
import boto3
import uuid
from botocore.client import Config
import asyncio
from ..core.config import settings

# Config variables
IS_DEVELOPMENT = settings.IS_DEVELOPMENT  # False = LocalStack, True = AWS
REGION = settings.REGION
LOCALSTACK_ENDPOINT = settings.LOCALSTACK_ENDPOINT

# Bucket names
PRODUCT_BUCKET = "product-images"
PROFILE_BUCKET = "profile-info"

SIZE_OF_IMAGE = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # Convert MB to bytes

# Initialize S3 client (reversed logic per your request)
if not IS_DEVELOPMENT:
    # Use LocalStack when IS_DEVELOPMENT is False
    s3 = boto3.client(
        "s3",
        endpoint_url=LOCALSTACK_ENDPOINT,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=REGION,
        config=Config(signature_version="s3v4"),
    )
else:
    # Use AWS S3 when IS_DEVELOPMENT is True
    s3 = boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=REGION,
    )


# Ensure buckets exist (only for LocalStack)
def ensure_buckets_exist():
    if IS_DEVELOPMENT:
        return  # Skip bucket creation in AWS

    existing_buckets = [b["Name"] for b in s3.list_buckets().get("Buckets", [])]
    for bucket in [PRODUCT_BUCKET, PROFILE_BUCKET]:
        if bucket not in existing_buckets:
            s3.create_bucket(Bucket=bucket)
            print(f"Created bucket: {bucket}")


# Upload file to S3 and return presigned URL
async def save_file_to_s3(file: UploadFile, bucket_name: str) -> str:
    ensure_buckets_exist()

    key = f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()
    if len(content) > SIZE_OF_IMAGE:
        raise ValueError("File size exceeds limit")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        lambda: s3.put_object(
            Bucket=bucket_name,
            Key=key,
            Body=content,
            ContentType=file.content_type,
        ),
    )

    signed_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=300,
    )

    return signed_url


# Bucket-specific upload wrappers
async def save_product_image(file: UploadFile) -> str:
    return await save_file_to_s3(file, PRODUCT_BUCKET)


async def save_profile_info(file: UploadFile) -> str:
    return await save_file_to_s3(file, PROFILE_BUCKET)
