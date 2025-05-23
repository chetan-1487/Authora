from fastapi import UploadFile
import boto3
import uuid
from botocore.client import Config
import asyncio

LOCALSTACK_ENDPOINT = "http://localhost:4566"
BUCKET_NAME = "product-images"
REGION = "us-east-1"

s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name=REGION,
    config=Config(signature_version="s3v4"),
)


# Ensure the bucket exists
def ensure_bucket_exists():
    existing_buckets = s3.list_buckets().get("Buckets", [])
    if not any(bucket["Name"] == BUCKET_NAME for bucket in existing_buckets):
        s3.create_bucket(Bucket=BUCKET_NAME)
        print(f"Created bucket: {BUCKET_NAME}")


# Async save product image to S3
async def save_product_image(file: UploadFile) -> str:
    ensure_bucket_exists()  # Make sure bucket exists

    key = f"{uuid.uuid4()}_{file.filename}"
    content = await file.read()

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(
        None,
        lambda: s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=content,
            ContentType=file.content_type,
        ),
    )

    signed_url = s3.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": BUCKET_NAME, "Key": key},
        ExpiresIn=300,
    )

    return signed_url
