from enum import Enum


class Table(str, Enum):
    CHATS = "chats"
    CREDITS = "credits"
    INVITATION = "invitation"
    QUESTION = "question"
    REFEREE_LIST = "referee_list"
    SHARED_CHATS = "shared_chats"
    URL_PLATFORMS = "url_platforms"
    USER_PROFILE = "user_profile"


class ChatColumn(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    PAYLOAD = "payload"
    IMAGE_STR = "image_str"
    LEARNER_MODE = "learner_mode"
    USER_ID = "user_id"
    THUMBNAIL_STR = "thumbnail_str"
    QUESTION = "question"
    TEXT_PROMPT = "text_prompt"
    IMAGE_CONTENT = "image_content"
    WOLFRAM_QUERY = "wolfram_query"
    WOLFRAM_ANSWER = "wolfram_answer"
    WOLFRAM_IMAGE = "wolfram_image"


class CreditColumn(str, Enum):
    TEMP_CREDIT = "temp_credit"
    PERM_CREDIT = "perm_credit"
    USER_ID = "user_id"
    ID = "id"
    LAST_AWARD_TIME = "last_award_time"


class InvitationColumn(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    USER_ID = "user_id"
    VALID_UNTIL = "valid_until"


class QuestionColumn(str, Enum):
    QUESTION_ID = "question_id"
    IMAGE_STR = "image_str"
    QUESTION = "question"


class RefereeColumn(str, Enum):
    GUEST_EMAIL = "guest_email"
    JOIN_DATE = "join_date"
    BONUS = "bonus"
    REFERRER_ID = "referral_id"
    IS_NOTIFY = "isNotify"


class SharedChatColumn(str, Enum):
    ID = "id"
    ...


class UrlPlatformColumn(str, Enum):
    ID = "id"
    CREATED_AT = "created_at"
    PLATFORM = "platform"
    CLICKS = "clicks"
    PLATFORM_ID = "platform_id"


class UserProfileColumn(str, Enum):
    USER_ID = "user_id"
    CREATED_AT = "created_at"
    USER_EMAIL = "user_email"
    IS_REWARDED = "is_rewarded"
    PLATFORM_ID = "platform_id"
