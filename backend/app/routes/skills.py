from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/skills",
    tags=["Skills"]
)


class Skill(BaseModel):
    name: str
    category: str


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
TECHNICAL_SKILLS = [
    "python",
    "numpy",
    "pandas",
    "matplotlib",
    "seaborn",
    "flask",
    "sql",
    "scikit-learn",
    "sklearn",
    "html",
    "css",
    "javascript",
    "react",
    "node.js",
    "machine learning",
    "deep learning",
    "tensorflow",
    "pytorch",
    "git",
    "github",
    "mongodb",
    "mysql",
    "fastapi"
]


def extract_skills(text: str):
    text = text.lower()

    found_skills = []

    for skill in TECHNICAL_SKILLS:
        if skill in text:
            found_skills.append(skill)

    return sorted(set(found_skills))