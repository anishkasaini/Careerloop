from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.schemas.opportunities import OpportunityCreate, OpportunityUpdate
from app.core.security import get_current_user, require_role
from app.supabase_client import supabase

router = APIRouter(
    prefix="/opportunities",
    tags=["Opportunities"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_opportunity(
    data: OpportunityCreate,
    current_user: dict = Depends(require_role("industry"))
):
    opportunity_payload = {
        "title": data.title,
        "company": data.company,
        "description": data.description,
        "opportunity_type": data.opportunity_type,
        "required_skills": data.required_skills,
        "location": data.location,
        "experience_required": data.experience_required,
        "deadline": data.deadline,
        "posted_by": current_user["email"],
        "status": "open"
    }

    result = (
        supabase
        .table("opportunities")
        .insert(opportunity_payload)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create opportunity"
        )

    return {
        "message": "Opportunity created successfully",
        "opportunity": result.data[0]
    }


@router.get("/")
def get_all_opportunities(
    current_user: dict = Depends(get_current_user)
):
    result = (
        supabase
        .table("opportunities")
        .select("*")
        .execute()
    )

    return {
        "opportunities": result.data if result.data else []
    }


@router.get("/{opportunity_id}")
def get_opportunity_by_id(
    opportunity_id: str,
    current_user: dict = Depends(get_current_user)
):
    result = (
        supabase
        .table("opportunities")
        .select("*")
        .eq("id", opportunity_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    return result.data[0]


@router.put("/{opportunity_id}")
def update_opportunity(
    opportunity_id: str,
    data: OpportunityUpdate,
    current_user: dict = Depends(require_role("industry"))
):
    # Check if opportunity exists
    existing = (
        supabase
        .table("opportunities")
        .select("*")
        .eq("id", opportunity_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    update_payload = {
        k: v for k, v in data.model_dump().items() if v is not None
    }

    if not update_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )

    result = (
        supabase
        .table("opportunities")
        .update(update_payload)
        .eq("id", opportunity_id)
        .execute()
    )

    return {
        "message": "Opportunity updated successfully",
        "opportunity": result.data[0] if result.data else existing.data[0]
    }


@router.delete("/{opportunity_id}")
def delete_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(require_role("industry"))
):
    # Check if opportunity exists
    existing = (
        supabase
        .table("opportunities")
        .select("*")
        .eq("id", opportunity_id)
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    supabase.table("opportunities").delete().eq("id", opportunity_id).execute()

    return {
        "message": "Opportunity deleted successfully"
    }
