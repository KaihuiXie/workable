from common.objects import supabase


class Supabase:
    def __init__(self):
        self.supabase = supabase

    def client(self):
        return self.supabase
