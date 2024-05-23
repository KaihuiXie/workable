from src.math_agent.supabase import Supabase


def clean_platform_text(platform: str) -> str:
    return platform.strip().upper()


class UrlPlatformsSupabase(Supabase):
    def __init__(self, supabase: Supabase):
        self.supabase = supabase.client()
        self.table = "url_platforms"

    def get_platform_id(self, platform: str) -> any:
        try:
            platform_cleaned = clean_platform_text(platform)
            data, count = (
                self.supabase.from_(self.table)
                .select("*")
                .eq("platform", platform_cleaned)
                .execute()
            )
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                return None
        except Exception as e:
            raise Exception(
                f"An error occurred during getting url platform({platform}) : {e}"
            )

    def add_new_platform(self, platform: str) -> str:
        try:
            platform_cleaned = clean_platform_text(platform)
            row_dict = {
                "platform": platform_cleaned,
            }
            data, count = self.supabase.table(self.table).insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during creating a new url platform: {e}"
            )

    def get_platform_id(self, platform: str) -> any:
        """
        Get platform_id. Create one if not exists.
        """
        try:
            platform_cleaned = clean_platform_text(platform)
            data, count = (
                self.supabase.from_(self.table)
                .select("*")
                .eq("platform", platform_cleaned)
                .execute()
            )
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                return self.add_new_platform(platform)
        except Exception as e:
            raise Exception(
                f"An error occurred during getting url platform({platform}) : {e}"
            )

    def delete_platform_by_id(self, platform_id: str) -> any:
        try:
            response = (
                self.supabase.table(self.table).delete().eq("id", platform_id).execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting platform {platform_id}: {e}"
            )

    def update_clicks(self, platform_id: str, value: int) -> int:
        try:
            data, count = (
                self.supabase.from_(self.table)
                .update({"clicks": value})
                .eq("id", platform_id)
                .execute()
            )
            return data[1][0]["clicks"]
        except Exception as e:
            raise Exception(
                f"An error occurred during updating clicks for platform {platform_id}: {e}"
            )

    def get_clicks_by_id(self, platform_id: str) -> any:
        try:
            data, count = (
                self.supabase.from_(self.table)
                .select("clicks")
                .eq("id", platform_id)
                .execute()
            )
            return data[1][0]["clicks"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting clicks for platform {platform_id}: {e}"
            )

    def increment_clicks(self, platform_id: str) -> int:
        try:
            old_value = self.get_clicks_by_id(platform_id)
            return self.update_clicks(platform_id, old_value + 1)
        except Exception as e:
            raise Exception(
                f"An error occurred during incrementing clicks for platform: {e}"
            )

    def update_platform_id_in_user_profile(self, user_id: str, platform_id: str) -> str:
        try:
            data, count = (
                self.supabase.from_("user_profile")
                .update({"platform_id": platform_id})
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["platform_id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during updating platform_id for user {user_id}: {e}"
            )

    def get_platform_id_by_user_id(self, user_id: str):
        try:
            data, count = (
                self.supabase.from_("user_profile")
                .select("platform_id")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["platform_id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting platform_id for user {user_id}: {e}"
            )
