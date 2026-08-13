import os
import shutil
from pathlib import Path

from fastapi import Depends, APIRouter, Form, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from app.schemas import ImageProcessionOptions
from app.users import current_active_user
from app.db import User
from app.utils import process_file


file_router = APIRouter()

UPLOAD_DIR = "/tmp" if os.environ.get("VERCEL") else "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@file_router.post("/upload/")
async def upload_file(
    file: UploadFile = File(...),
    resize: str = Form(None),
    convert_to: str = Form(None),
    grayscale: bool = Form(None),
    flip: str = Form(None),
    user: User = Depends(current_active_user)
):
    options = ImageProcessionOptions(
        resize=resize,
        convert_to=convert_to,
        grayscale=grayscale,
        flip=flip,
    )

    user_folder = os.path.join(UPLOAD_DIR, str(user.id))
    os.makedirs(user_folder, exist_ok=True)

    file_location = os.path.join(user_folder, str(file.filename))

    with open(file_location, "wb") as buffers:
        shutil.copyfileobj(file.file, buffers)

    processed_file_location = process_file(file_location, options)
    
    # Зверніть увагу: повертаємо базове ім'я файлу (воно може змінитись після конвертації, наприклад .png -> .jpg)
    return {
        "filename": os.path.basename(processed_file_location), 
        "location": processed_file_location
    }


@file_router.get("/download/{filename}", response_class=FileResponse)
async def download_file(filename: str, user: User = Depends(current_active_user)):
    user_folder = os.path.join(UPLOAD_DIR, str(user.id))
    file_location = os.path.join(user_folder, filename)
    
    if not os.path.exists(file_location):
        raise HTTPException(status_code=404, detail="File not found")
        
    return FileResponse(file_location)
