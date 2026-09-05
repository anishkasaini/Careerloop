from fastapi import APIRouter, UploadFile, File
from pypdf import PdfReader
import io

from app.routes.skills import extract_skills

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    file_content = await file.read()

    reader = PdfReader(io.BytesIO(file_content))

    text = ""

    for page in reader.pages:
        extracted_text = page.extract_text()
        if extracted_text:
            text += extracted_text + "\n"

    detected_skills = extract_skills(text)

    return {
        "message": "Resume processed successfully",
        "filename": file.filename,
        "skills": detected_skills,
        "text": text
    }