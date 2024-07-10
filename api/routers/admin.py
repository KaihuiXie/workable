import logging

from fastapi import APIRouter, HTTPException

from common.objects import admin
from src.admin.interfaces import InviteByEmailRequest, InviteByEmailResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/invite_user_by_email", response_model=InviteByEmailResponse)
async def invite_user_by_email(request: InviteByEmailRequest) -> InviteByEmailResponse:
    try:
        user_id = admin.invite_user_by_email(request.email, request.redirect_to_url)
        return InviteByEmailResponse(user_id=user_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))
