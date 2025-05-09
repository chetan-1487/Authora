from sqlalchemy.orm import Session
from fastapi import UploadFile
from io import BytesIO
from PIL import Image
import os
import uuid
from app.api.v1.auth.model import User

UPLOAD_DIR = "./uploaded_images/"

# Create the directory if it doesn't exist
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


def save_profile_picture(profile_picture: UploadFile, existing_filename: str = None):
    # Read the file content from the UploadFile object
    file_content = profile_picture.file.read()

    # Open the image from the uploaded content
    image = Image.open(BytesIO(file_content))

    # Determine the file extension (use the format from the image)
    file_extension = image.format.lower()

    # Generate a unique filename using uuid if it's a new image
    unique_filename = f"{uuid.uuid4()}.{file_extension}" if existing_filename is None else existing_filename
    
    # Full path for saving the image
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save the image to the generated file path
    image.save(file_path, format=image.format)

    return unique_filename


def update_user(db: Session, user_id: str, profile_picture: UploadFile = None):
    # Fetch the current user from the database
    user = db.query(User).filter(User.id == user_id).first()

    if user:
        if profile_picture:
            # If the profile picture is being updated, save the new image
            profile_picture_name = save_profile_picture(profile_picture, existing_filename=user.profile_picture)
            user.profile_picture = profile_picture_name
        
        # Here you would update other fields (like name, email, etc.) if needed:
        # Example: user.name = data.name
        db.commit()  # Commit the transaction to the database
        db.refresh(user)  # Refresh to get the updated user
    
    return user
