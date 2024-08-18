import logging

from src.url_platforms.interfaces import (
    IncrementClicksRequest,
    IncrementClicksResponse,
    UpdateUserProfilePlatformIdRequest,
    UpdateUserProfilePlatformIdResponse,
)
from src.url_platforms.supabase import UrlPlatformsSupabase

# Configure logging
logging.basicConfig(level=logging.INFO)


class UrlPlatforms(UrlPlatformsSupabase):
    def __init__(self, supabase):
        self.supabase:UrlPlatformsSupabase = supabase

    def get_platform_id(self, platform: str) -> str:
        return self.supabase.get_platform_id(platform)

    def increment_clicks(
        self, request: IncrementClicksRequest
    ) -> IncrementClicksResponse:
        clicks = self.supabase.increment_clicks(request.platform_id)
        response: IncrementClicksResponse = {"clicks": clicks}
        return response

    def update_platform_id(
        self, request: UpdateUserProfilePlatformIdRequest
    ) -> UpdateUserProfilePlatformIdResponse:
        if request.platform_id:
            platform_id = self.supabase.update_platform_id_in_user_profile(
                request.user_id, request.platform_id
            )
        response: UpdateUserProfilePlatformIdResponse = {"platform_id": request.platform_id}
        return response
