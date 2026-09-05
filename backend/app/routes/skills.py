from fastapi import APIRouter
from pydantic import BaseModel

from app.core.extraction import extract_skills_from_text, EXTRACTION_TAXONOMY

router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


class Skill(BaseModel):
    name: str
    category: str


class JobDescriptionRequest(BaseModel):
    job_description: str


skills = []


@router.post("/")
def add_skill(skill: Skill):
    skill_data = {
        "id": len(skills) + 1,
        **skill.model_dump()
    }

    skills.append(skill_data)

    return {
        "message": "Skill added successfully",
        "skill": skill_data
    }


@router.get("/")
def get_skills():
    return {
        "skills": skills
    }


@router.post("/extract-jd")
def extract_jd_skills(data: JobDescriptionRequest):
    extracted = extract_skills_from_text(data.job_description)
    return {
        "extracted_skills": extracted,
        "total_count": len(extracted)
    }


# Retained for backward compatibility
TECHNICAL_SKILLS = EXTRACTION_TAXONOMY


def extract_skills(text: str):
    """
    Extracts tech skills from text using boundary-aware matching and normalization.
    Fully backward compatible with resume.py.
    """
    return extract_skills_from_text(text)