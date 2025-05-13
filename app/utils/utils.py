from sqlalchemy.orm import Session
from fastapi import UploadFile
from io import BytesIO
from PIL import Image
import os
import uuid
import requests
from app.api.v1.auth.model import User

UPLOAD_DIR = "./uploaded_images/"

# Create the upload directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def save_profile_picture(profile_picture: UploadFile, existing_filename: str = None):
    file_content = profile_picture.file.read()
    image = Image.open(BytesIO(file_content))

    file_extension = image.format.lower()
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    image.save(file_path, format=image.format)
    return unique_filename

def save_profile_picture_from_url(profile_picture_url: str, existing_filename: str = None):
    if not profile_picture_url:
        return None

    try:
        response = requests.get(profile_picture_url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))
        file_extension = image.format.lower()
        unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
        file_path = os.path.join(UPLOAD_DIR, unique_filename)

        image.save(file_path, format=image.format)
        return unique_filename
    except Exception as e:
        print("Error saving profile picture from URL:", e)
        return None
