from supabase import create_client, Client, ClientOptions
from datetime import datetime, timezone
from common.constant import TIME_FORMAT
import datetime as dt
import dateutil.parser


from common.constant import (
    EVERY_DAY_CREDIT_INCREMENT,
    COST_PER_QUESTION,
    DEFAULT_CREDIT,
    INVITATION_TOKEN_EXPIRATION,
    INVITATION_BONUES,
)

from src.utils import generate_thumbnail_string_from_image_string


def is_same_day(date: datetime):
    return date.date() == datetime.utcnow().date()


def is_invitation_expired(timestamp):
    invitation_expiration = dateutil.parser.parse(timestamp)
    now = datetime.now(timezone.utc)
    # if now is greater than invitation expiration, then it is expired
    return now > invitation_expiration


class Supabase:
    def __init__(self, url, key):
        self.supabase: Client = create_client(
            url, key, options=ClientOptions(flow_type="pkce")
        )

    def client(self):
        return self.supabase

    def auth(self):
        return self.auth

    def sign_up(self, email: str, phone: str, password: str):
        try:
            res = self.supabase.auth.sign_up(
                {"email": email, "phone": phone, "password": password}
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing up user with email {email}: {e}"
            )

    def sign_in_with_password(self, email: str, phone: str, password: str):
        try:
            res = self.supabase.auth.sign_in_with_password(
                {"email": email, "phone": phone, "password": password}
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with email {email}: {e}"
            )

    def sign_in_with_oauth(self, provider: str):
        try:
            res = self.supabase.auth.sign_in_with_oauth(
                {
                    "provider": provider,
                }
            )
            return res
        except Exception as e:
            raise Exception(
                f"An error occurred during signing in user with oauth provider {provider}: {e}"
            )

    def sign_out(self):
        try:
            res = self.supabase.auth.sign_out()
            return res
        except Exception as e:
            raise Exception(f"An error occurred during signing out: {e}")

    def get_session(self):
        try:
            session = self.supabase.auth.get_session()
            return session
        except Exception as e:
            raise Exception(f"An error occurred during getting session: {e}")

    def get_chat_payload_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("payload")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["payload"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat payload by chat_id {chat_id}: {e}"
            )

    def get_chat_image_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("image_str")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["image_str"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting question image by chat_id {chat_id}: {e}"
            )

    def get_chat_question_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("question")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["question"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat question by chat_id {chat_id}: {e}"
            )

    def get_chat_by_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats").select("*").eq("id", chat_id).execute()
            )
            return data[1][0]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting chat question by chat_id {chat_id}: {e}"
            )

    def create_empty_chat(self, user_id):
        try:
            row_dict = {
                "image_str": "",
                "thumbnail_str": "",
                "user_id": user_id,
                "question": "",
                "payload": "",
                "learner_mode": False,
            }
            data, count = self.supabase.table("chats").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating an empty chat: {e}")

    def fulfill_empty_chat(
        self, chat_id, image_str, thumbnail_str, question, is_learner_mode
    ):
        try:
            payload = self.question_to_payload(question)
            response = (
                self.supabase.table("chats")
                .update(
                    {
                        "image_str": image_str,
                        "thumbnail_str": thumbnail_str,
                        "payload": payload,
                        "question": question,
                        "learner_mode": is_learner_mode,
                    }
                )
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during fulfill fields for chat {chat_id}: {e}"
            )

    def create_shared_chat(
        self,
        user_id,
        chat_id,
        updated_at,
        payload,
        image_str,
        question,
        thumbnail_str,
        learner_mode,
        is_permanent=False,
    ):
        try:
            row_dict = {
                "user_id": user_id,
                "chat_id": chat_id,
                "updated_at": updated_at,
                "payload": payload,
                "image_str": image_str,
                "question": question,
                "thumbnail_str": thumbnail_str,
                "leaner_mode": learner_mode,
                "is_permanent": is_permanent,
            }
            data, count = self.supabase.table("shared_chats").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating a shared chat: {e}")

    def delete_shared_chat_by_shared_chat_id(self, shared_chat_id):
        try:
            response = (
                self.supabase.table("shared_chats")
                .delete()
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting shared chat {shared_chat_id}: {e}"
            )

    def delete_shared_chat_by_chat_id(self, chat_id):
        """Delete all shared_chat(s) linked to the chat specified by chat_id."""
        try:
            response = (
                self.supabase.table("shared_chats")
                .delete()
                .eq("chat_id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting shared chats {chat_id}: {e}"
            )

    def get_shared_chat_by_shared_chat_id(self, shared_chat_id):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("*")
                .eq("id", shared_chat_id)
                .execute()
            )
            return data[1][0]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by shared_chat_id {shared_chat_id}: {e}"
            )

    def get_shared_chats_by_chat_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("*")
                .eq("chat_id", chat_id)
                .execute()
            )
            return data[1]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by chat_id {chat_id}: {e}"
            )

    def update_shared_chat_create_time_to_now(self, shared_chat_id):
        try:
            response = (
                self.supabase.table("shared_chats")
                .update(
                    {"created_at": datetime.now(timezone.utc).strftime(TIME_FORMAT)}
                )
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating create time for shared chat {shared_chat_id}: {e}"
            )

    def update_shared_chat_create_time(self, shared_chat_id, updated_at):
        try:
            response = (
                self.supabase.table("shared_chats")
                .update({"created_at": updated_at})
                .eq("id", shared_chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating create time for shared chat {shared_chat_id}: {e}"
            )

    def get_shared_chat_by_chat_id_updated_time(self, chat_id, updated_at):
        try:
            data, count = (
                self.supabase.from_("shared_chats")
                .select("id")
                .eq("chat_id", chat_id)
                .eq("updated_at", updated_at)
                .execute()
            )
            if len(data[1]) == 0:
                return None
            else:
                return data[1][0]["id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting shared chat by chat_id {chat_id} and updated_at {updated_at}: {e}"
            )

    def get_all_chats(self, user_id):
        try:
            response = (
                self.supabase.from_("chats")
                .select(
                    "id, thumbnail_str, question, learner_mode, created_at",
                    count="exact",
                )
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .execute()
            )
            self.grant_login_award(user_id)
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting all chats for user {user_id}: {e}"
            )

    def backfill_thumbnail_str(self, chat_ids):
        for chat_id in chat_ids:
            try:
                data, count = (
                    self.supabase.from_("chats")
                    .select("thumbnail_str, image_str", count="exact")
                    .eq("id", chat_id)
                    .execute()
                )

                if not data[1][0]["thumbnail_str"] and data[1][0]["image_str"]:
                    print("Backfill thumbnail_str")
                    thumbnail_str = generate_thumbnail_string_from_image_string(
                        data[1][0]["image_str"]
                    )
                    self.update_thumbnail(chat_id, thumbnail_str)
            except Exception as e:
                raise Exception(
                    f"An error occurred during backfilling thumbnail for chat {chat_id}: {e}"
                )

    def get_chats_by_ids(self, chat_ids):
        try:
            response = (
                self.supabase.from_("chats")
                .select("id, thumbnail_str, question, learner_mode", count="exact")
                .in_("id", chat_ids)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred getting chats for chat_ids {chat_ids}: {e}"
            )

    def update_payload(self, chat_id, payload):
        try:
            response = (
                self.supabase.table("chats")
                .update({"payload": payload})
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during upserting payload for chat {chat_id}: {e}"
            )

    def update_thumbnail(self, chat_id, thumbnail_str):
        try:
            response = (
                self.supabase.table("chats")
                .update({"thumbnail_str": thumbnail_str})
                .eq("id", chat_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating thumbnail_str for chat {chat_id}: {e}"
            )

    def delete_chat_by_id(self, chat_id):
        try:
            response = self.supabase.table("chats").delete().eq("id", chat_id).execute()
            return response
        except Exception as e:
            raise Exception(f"An error occurred during deleting chat {chat_id}: {e}")

    @staticmethod
    def question_to_payload(question):
        message = [{"role": "assistant", "content": question}]
        payload = {"messages": message}
        return payload

    # for everyday login & refresh every Sunday
    def update_temp_credit_by_user_id(self, user_id, amount):
        try:
            if amount < 0:
                raise ValueError(f"User {user_id}: credit can't be negative.")
            response = (
                self.supabase.table("credits")
                .update({"temp_credit": amount})
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating temp credit for user {user_id}: {e}"
            )

    # for invitations and purchases
    def update_perm_credit_by_user_id(self, user_id, amount):
        try:
            if amount < 0:
                raise ValueError(f"User {user_id}: credit can't be negative.")
            response = (
                self.supabase.table("credits")
                .update({"perm_credit": amount})
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating perm credit for user {user_id}: {e}"
            )

    def get_temp_credit_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("temp_credit")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["temp_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting temp credit by user {user_id}: {e}"
            )

    def get_perm_credit_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("perm_credit")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["perm_credit"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting perm credit by user {user_id}: {e}"
            )

    def get_credit_by_user_id(self, user_id):
        try:
            return self.get_temp_credit_by_user_id(
                user_id
            ) + self.get_perm_credit_by_user_id(user_id)
        except Exception as e:
            raise Exception(
                f"An error occurred during getting credit by user {user_id}: {e}"
            )

    def get_user_id_by_chat_id(self, chat_id):
        try:
            data, count = (
                self.supabase.from_("chats")
                .select("user_id")
                .eq("id", chat_id)
                .execute()
            )
            return data[1][0]["user_id"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting user_id by chat {chat_id}: {e}"
            )

    def decrement_credit(self, user_id):
        try:
            temp_credit = self.get_temp_credit_by_user_id(user_id)
            perm_credit = self.get_perm_credit_by_user_id(user_id)
            if temp_credit >= COST_PER_QUESTION:
                self.update_temp_credit_by_user_id(
                    user_id, temp_credit - COST_PER_QUESTION
                )
            elif perm_credit >= COST_PER_QUESTION:
                self.update_perm_credit_by_user_id(
                    user_id, perm_credit - COST_PER_QUESTION
                )
            else:
                raise ValueError(
                    f"User {user_id}: {user_id} doesn't have enough credits."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during decrement credit from user {user_id}: {e}"
            )

    def create_credit(self, user_id):
        try:
            row_dict = {
                "user_id": user_id,
                "temp_credit": DEFAULT_CREDIT,
                "perm_credit": DEFAULT_CREDIT,
                "last_award_time": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
            }
            data, count = self.supabase.table("credits").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(f"An error occurred during creating a user credit: {e}")

    def get_last_sign_in_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("last_sign_in_at")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["last_sign_in_at"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user email {user_id}: {e}"
            )

    # 1. Check if user is eligible for login award
    # 1.1 get last_award_time
    # 1.2 compare with today
    # 2. if 1 is yes
    # 2.1 get_prev_temp_credit
    # 2.2 update_temp_credit
    # 2.3 update last_award_time
    def grant_login_award(self, user_id):
        last_award_time = self.get_last_award_time_by_user_id(user_id)
        is_eligible = not is_same_day(dateutil.parser.parse(last_award_time))
        if not is_eligible:
            return
        prev_temp_credit = self.get_temp_credit_by_user_id(user_id)
        self.update_temp_credit_by_user_id(
            user_id, prev_temp_credit + EVERY_DAY_CREDIT_INCREMENT
        )
        self.update_last_award_time_by_user_id(user_id)

    def get_bonus(self, user_id):
        prev_perm_credit = self.get_perm_credit_by_user_id(user_id)
        self.update_perm_credit_by_user_id(
            user_id, prev_perm_credit + INVITATION_BONUES
        )

    def update_last_award_time_by_user_id(self, user_id):
        try:
            response = (
                self.supabase.table("credits")
                .update(
                    {
                        "last_award_time": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%dT%H:%M:%S%z"
                        )
                    }
                )
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during updating perm credit for user {user_id}: {e}"
            )

    def get_last_award_time_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("credits")
                .select("last_award_time")
                .eq("user_id", user_id)
                .execute()
            )
            return data[1][0]["last_award_time"]
        except Exception as e:
            raise Exception(
                f"An error occurred during getting last login by user email {user_id}: {e}"
            )

    def get_invitation_by_user_id(self, user_id):
        try:
            data, count = (
                self.supabase.from_("invitation")
                .select("id, valid_until")
                .eq("user_id", user_id)
                .execute()
            )

            # case1, if token does not exist, then create a new token
            if len(data[1]) == 0 or not data[1]:
                return self.create_invitation(user_id)

            token = data[1][0]["id"]
            expiration = data[1][0]["valid_until"]

            # case2: if token expired, delete the old one, and then create a new token
            if is_invitation_expired(expiration):
                self.delete_invitation_by_user_id(user_id)
                return self.create_invitation(user_id)

            # case3: return a valid token
            return token
        except Exception as e:
            raise Exception(
                f"An error occurred during getting invitation by user {user_id}: {e}"
            )

    def create_invitation(self, user_id):
        try:
            row_dict = {
                "user_id": user_id,
                "created_at": datetime.now(timezone.utc).strftime(
                    "%Y-%m-%dT%H:%M:%S%z"
                ),
                "valid_until": (
                    datetime.now(timezone.utc)
                    + dt.timedelta(days=INVITATION_TOKEN_EXPIRATION)
                ).strftime("%Y-%m-%dT%H:%M:%S%z"),
            }
            data, count = self.supabase.table("invitation").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]["id"]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during creating invitation for user {user_id}: {e}"
            )

    def is_eligible_for_reward(self, token, user_id):
        try:
            data, count = (
                self.supabase.table("user_profile")
                .select("is_rewarded", "created_at", "user_email")
                .eq("user_id", user_id)
                .execute()
            )
            is_rewarded, created_at, user_email = (
                data[1][0]["is_rewarded"],
                data[1][0]["created_at"],
                data[1][0]["user_email"],
            )
            data, count = (
                self.supabase.table("invitation")
                .select("created_at")
                .eq("id", token)
                .execute()
            )
            token_date = data[1][0]["created_at"]
            if is_rewarded:
                return False, user_email
            if token_date < created_at:
                return False, user_email
            self.supabase.table("user_profile").update({"is_rewarded": True}).eq(
                "user_id", user_id
            ).execute()
            return True, user_email
        except Exception as e:
            raise Exception(
                f"An error occurred during getting information from user_id {user_id}: {e}"
            )

    def get_referee_list(self, user_id):
        try:
            response = (
                self.supabase.table("referee_list")
                .select("referrer_id, guest_email, join_date, bonus")
                .eq("referrer_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting invitation for user {user_id}: {e}"
            )

    def update_referee_list(self, user_id, guest_email):
        try:
            row_dict = {
                "referrer_id": user_id,
                "guest_email": guest_email,
                "join_date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z"),
                "bonus": INVITATION_BONUES,
            }
            data, count = self.supabase.table("referee_list").insert(row_dict).execute()
            # Check if exactly one record was inserted
            if len(data[1]) == 1:
                return data[1][0]
            else:
                raise ValueError(
                    f"Unexpected number of records inserted: {len(data)}. Expected 1."
                )
        except Exception as e:
            raise Exception(
                f"An error occurred during updateing referee list for user {user_id} and guest {guest_email}: {e}"
            )

    def delete_invitation_by_user_id(self, user_id):
        try:
            response = (
                self.supabase.table("invitation")
                .delete()
                .eq("user_id", user_id)
                .execute()
            )
            return response
        except Exception as e:
            raise Exception(
                f"An error occurred during deleting invitation for user {user_id}: {e}"
            )

    def get_referrer_id_by_invitation_token(self, token):
        if token == "":
            return False, ""
        try:
            data, count = (
                self.supabase.from_("invitation")
                .select("user_id, valid_until")
                .eq("id", token)
                .execute()
            )

            user_id = data[1][0]["user_id"]
            expiration = data[1][0]["valid_until"]

            if is_invitation_expired(expiration):
                return False, user_id
            return True, user_id
        except Exception as e:
            return False, ""
