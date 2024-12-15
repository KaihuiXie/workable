from supabase import Client, create_client

class ResumeSupabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(url, key)