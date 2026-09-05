from pydantic import BaseModel
from typing import List, Optional, Literal


class OpportunityCreate(BaseModel):
    title: str
    company: str
    description: str
    opportunity_type: Literal["job", "internship"]
    required_skills: List[str]
    location: str
    experience_required: str
    deadline: str


class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    opportunity_type: Optional[Literal["job", "internship"]] = None
    required_skills: Optional[List[str]] = None
    location: Optional[str] = None
    experience_required: Optional[str] = None
    deadline: Optional[str] = None
