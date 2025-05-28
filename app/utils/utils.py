import random
import string
from fastapi import UploadFile
import httpx


# OTP Generator
def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


class DummyUploadFile:
    def __init__(self, content: bytes, filename: str, content_type: str):
        self.content = content
        self.filename = filename
        self.content_type = content_type

    async def read(self):
        return self.content


async def download_image_as_upload_file(url: str) -> UploadFile:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "image/jpeg")
        filename = url.split("/")[-1].split("?")[0]

        return DummyUploadFile(
            content=response.content,
            filename=filename or "profile.jpg",
            content_type=content_type,
        )
