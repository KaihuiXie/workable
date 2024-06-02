import os
import re

from dotenv import load_dotenv

from flumes.split_chats_table_question.split_chats_table_question_supabase import SplitChatsTableQuestionSupabase


def search(question, tag):
    pattern = rf"<{tag}>((.|[\r\n])*?)</{tag}>"
    match = re.search(pattern, question, re.DOTALL)
    if match and match.group(1) != "None":
        print(f"{tag}: {match.group(1)}")
        return match.group(1)
    print(f"{tag}: None")
    return None


def split_rows_created_after(created_timestamp):
    load_dotenv()
    supabase = SplitChatsTableQuestionSupabase(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    all_chats = supabase.get_all_chats_created_after(created_timestamp)
    count = len(all_chats)
    for i in range(count):
        chat = all_chats[i]
        old_question = chat["question"]
        chat_id = chat["id"]
        print(f"Processing {i}/{count}, chat_id: {chat_id}")

        new_question = search(old_question, "question")
        image_content = search(old_question, "image_content")
        text_prompt = search(old_question, "question_context")
        if text_prompt is None:
            text_prompt = search(old_question, "text_prompt")
        if new_question is None:
            new_question = old_question

        supabase.back_fill_new_columns(chat_id, new_question, text_prompt, image_content)


if __name__ == "__main__":
    split_after = "2024-06-02 07:22:04.774631+00"  # created_at of the last splitted row
    split_rows_created_after(split_after)
