from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/matching",
    tags=["Skill Matching"]
)


class MatchingRequest(BaseModel):
    student_skills: list[str]
    required_skills: list[str]


@router.post("/check")
def check_skill_match(data: MatchingRequest):
    student_skills = {
        skill.lower().strip()
        for skill in data.student_skills
    }

    required_skills = {
        skill.lower().strip()
        for skill in data.required_skills
    }

    matched_skills = student_skills.intersection(required_skills)
    missing_skills = required_skills - student_skills

    if required_skills:
        match_percentage = round(
            (len(matched_skills) / len(required_skills)) * 100,
            2
        )
    else:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }
@router.post("/resume-match")
def resume_match(
    student_skills: list[str],
    required_skills: list[str]
):
    student_skills = {
        skill.lower().strip()
        for skill in student_skills
    }

    required_skills = {
        skill.lower().strip()
        for skill in required_skills
    }

    matched_skills = student_skills.intersection(required_skills)
    missing_skills = required_skills - student_skills
    

    if required_skills:
        match_percentage = round(
            (len(matched_skills) / len(required_skills)) * 100,
            2
        )
    else:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }