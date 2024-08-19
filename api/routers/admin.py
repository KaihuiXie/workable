import logging

from fastapi import APIRouter, HTTPException

from common.objects import admin
from src.admin.interfaces import InviteByEmailRequest, InviteByEmailResponse, DeleteByEmailRequest, DeleteByEmailResponse

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/invite_user_by_email", response_model=InviteByEmailResponse)
def invite_user_by_email(request: InviteByEmailRequest) -> InviteByEmailResponse:
    try:
        user_id = admin.invite_user_by_email(request.email, request.redirect_to_url,request.invitation_token, request.platform_token)
        return InviteByEmailResponse(user_id=user_id)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))

@router.delete("/delete_user_by_email")
def invite_user_by_email(request: DeleteByEmailRequest):
    try:
        admin.delete_user_by_email(request.email)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=str(e.detail))