import logging

from fastapi import APIRouter, HTTPException

from common.objects import url_platforms
from src.url_platforms.interfaces import (
    IncrementClicksRequest,
    IncrementClicksResponse,
    UpdateUserProfilePlatformIdRequest,
    UpdateUserProfilePlatformIdResponse,
)

router = APIRouter(
    prefix="/url_platforms",
    tags=["url_platforms"],
    responses={404: {"description": "Not found"}},
)

logging.basicConfig(level=logging.INFO)


@router.post("/increment", response_model=IncrementClicksResponse)
async def increment_clicks(request: IncrementClicksRequest) -> IncrementClicksResponse:
    try:
        return url_platforms.increment_clicks(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update_user_profile", response_model=UpdateUserProfilePlatformIdResponse)
async def update_platform_id(request: UpdateUserProfilePlatformIdRequest):
    try:
        return url_platforms.update_platform_id(request)
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail=str(e))
