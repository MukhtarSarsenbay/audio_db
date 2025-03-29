from fastapi import APIRouter, UploadFile, File, Depends
import shutil
from app.auth import get_current_user

router = APIRouter()

UPLOAD_DIR = "uploads/"

@router.post("/upload/")
async def upload_audio(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user) 
):
    file_location = f"{UPLOAD_DIR}{file.filename}"
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "path": file_location}
