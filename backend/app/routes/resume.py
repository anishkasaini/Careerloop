from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pypdf import PdfReader
import io
import logging

from app.routes.skills import extract_skills

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/resume",
    tags=["Resume"]
)


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        if not file_content:
            return {
                "message": "Empty file provided",
                "filename": file.filename,
                "skills": [],
                "text": ""
            }

        reader = PdfReader(io.BytesIO(file_content))
        text = ""

        for page in reader.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"

        detected_skills = extract_skills(text) if text.strip() else []

        return {
            "message": "Resume processed successfully",
            "filename": file.filename,
            "skills": detected_skills,
            "text": text
        }
    except Exception as e:
        logger.warning(f"Error reading resume {file.filename}: {e}")
        return {
            "message": "Could not extract text from the provided file. Please ensure it is a valid, readable PDF.",
            "filename": file.filename or "unknown",
            "skills": [],
            "text": ""
        }