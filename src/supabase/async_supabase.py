from supabase import AClient, AClientOptions, acreate_client
from fastapi import HTTPException,status

class AsyncSupabase:
    def __init__(self, supabase_client: AClient):
        self.supabase = supabase_client
        
    @classmethod
    async def create(cls, url, key):
        supabase_client: AClient = await acreate_client(
            url, key, options=AClientOptions(flow_type="pkce")
        )
        return cls(supabase_client)

    async def update_premium(self, user_email, is_subscripe):
        try:
            data, count = (
                await self.supabase.from_("user_profile")
                .update(
                    {
                        "is_premium":is_subscripe
                    }
                )
                .eq("user_email", user_email)
                .execute()
            )
        except Exception as e:
            print(e)
            if str(e) == "A user with this email address not exist":
                raise HTTPException(
                    detail=f"{user_email}: {e}",
                    status_code=status.HTTP_409_CONFLICT,
                )
            else:
                raise HTTPException(
                    detail=f"{user_email}: {e}",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )