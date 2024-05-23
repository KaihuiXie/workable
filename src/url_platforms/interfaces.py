from pydantic import BaseModel


class IncrementClicksRequest(BaseModel):
    platform_id: str


class IncrementClicksResponse(BaseModel):
    clicks: int


class UpdateUserProfilePlatformIdRequest(BaseModel):
    user_id: str
    platform_id: str


class UpdateUserProfilePlatformIdResponse(BaseModel):
    platform_id: str
