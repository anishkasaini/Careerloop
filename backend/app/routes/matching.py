from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Optional

from app.core.normalization import normalize_skill_set
from app.core.semantic_matching import compute_semantic_matching
from app.core.skill_gap import analyze_skill_gap

router = APIRouter(
    prefix="/matching",
    tags=["Skill Matching"]
)


class MatchingRequest(BaseModel):
    student_skills: List[str]
    required_skills: List[str]


class SemanticMatchingRequest(BaseModel):
    student_skills: List[str]
    required_skills: List[str]
    similarity_threshold: Optional[float] = 0.55


class SkillGapRequest(BaseModel):
    student_skills: List[str]
    required_skills: List[str]
    similarity_threshold: Optional[float] = 0.55


@router.post("/check")
def check_skill_match(data: MatchingRequest):
    student_skills = normalize_skill_set(data.student_skills)
    required_skills = normalize_skill_set(data.required_skills)

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
    student_skills: List[str],
    required_skills: List[str]
):
    student_skills_set = normalize_skill_set(student_skills)
    required_skills_set = normalize_skill_set(required_skills)

    matched_skills = student_skills_set.intersection(required_skills_set)
    missing_skills = required_skills_set - student_skills_set

    if required_skills_set:
        match_percentage = round(
            (len(matched_skills) / len(required_skills_set)) * 100,
            2
        )
    else:
        match_percentage = 0

    return {
        "match_percentage": match_percentage,
        "matched_skills": sorted(matched_skills),
        "missing_skills": sorted(missing_skills)
    }


@router.post("/semantic-match")
def semantic_skill_match(data: SemanticMatchingRequest):
    threshold = data.similarity_threshold if data.similarity_threshold is not None else 0.55
    return compute_semantic_matching(
        student_skills=data.student_skills,
        required_skills=data.required_skills,
        similarity_threshold=threshold
    )


@router.post("/skill-gap")
def skill_gap(data: SkillGapRequest):
    threshold = data.similarity_threshold if data.similarity_threshold is not None else 0.55
    return analyze_skill_gap(
        student_skills=data.student_skills,
        required_skills=data.required_skills,
        similarity_threshold=threshold
    )