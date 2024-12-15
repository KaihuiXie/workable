from src.resume.supabase import ResumeSupabase

class Resume(ResumeSupabase):
    def __init__(self, supabase):
        self.supabase: ResumeSupabase = supabase