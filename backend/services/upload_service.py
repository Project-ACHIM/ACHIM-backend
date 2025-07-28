import uuid
import os
from fastapi import UploadFile
from backend.core.config import settings


def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    ext = file.filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    upload_path = os.path.join(settings.UPLOAD_DIR, filename)


    with open(upload_path, "wb") as buffer:
        buffer.write(file.file.read())

    url = f"/static/uploads/{filename}"
    return filename, url
