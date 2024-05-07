import unittest
from src.credits import supabase as cresupabase
from src.shared_chats import supabase as scsupabase


class SupabaseTest(unittest.TestCase):
    def test_supabase_object(self):
        credits_supabase = cresupabase.Supabase()
        shared_chats_supabase = scsupabase.Supabase()
        self.assertEqual(
            id(credits_supabase.client()), id(shared_chats_supabase.client())
        )


if __name__ == "__main__":
    unittest.main()
