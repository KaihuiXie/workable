import base64
import logging
import re

import requests
from PIL import Image
from openai import OpenAI

from common.decorators import TimerLogLevel, timer
from src.supabase.interfaces import ChatColumn
from src.math_agent.prompts import (
    IMAGE_READING_PROMPT,
    LANGUAGE_PROMPT,
    LATEX_PROMPT,
    QUESTION_CONTEXT_PROMPT,
    SYSTEM_PROMPT,
    WOLFRAM_ALPHA_SUMMARIZE_SYSTEM_PROMPT,
    WOLFRAM_ALPHA_SUMMARIZE_TEMPLATE,
    get_user_prompt_for_solve,
)
from src.supabase.supabase import Supabase
from src.math_agent.utils import replace_wolfram_image
from src.utils import bytes_to_base64

# Configure logging
logging.basicConfig(level=logging.INFO)


class MathAgent:
    def __init__(self, openai_api_keys: str, wolf_api_key, supabase: Supabase):
        self.open_ai_keys = [s.strip() for s in openai_api_keys.split(",")]
        self.wolf_api_key = wolf_api_key
        self.wolfram_url = "http://api.wolframalpha.com/v2/query"
        self.supabase = supabase

    def _get_openai_key(self):
        # Remove and get the first element
        cur_key = self.open_ai_keys.pop(0)
        # Append the first element to the end of the list
        self.open_ai_keys.append(cur_key)
        return cur_key

    def _cur_openai_client(self):
        return OpenAI(api_key=self._get_openai_key())

    def _compose_image_content(self, image_base64_str, text_prompt):
        return [
            {"type": "text", "text": text_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64_str}"},
            },
        ]

    @timer(log_level=TimerLogLevel.BASIC)
    def parse_question(self, image_base64_str, additional_prompt):
        session = self._cur_openai_client()
        Question_Context = QUESTION_CONTEXT_PROMPT.format(context=additional_prompt)
        content = self._compose_image_content(
            image_base64_str,
            IMAGE_READING_PROMPT.format(
                Question_Context=Question_Context, LATEX_PROMPT=LATEX_PROMPT
            ),
        )
        response = session.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": content}],
            max_tokens=1024,
            stop=["###SYSTEM_PROMPT"],
        )
        return response.choices[0].message.content

    @timer(log_level=TimerLogLevel.BASIC)
    def query(self, messages):
        session = self._cur_openai_client()
        stream = session.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            # temperature=0.1,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stop=["###SYSTEM_PROMPT"],
            stream=True,
        )
        return stream

    def _extract_wolfram_image(self, wolfram_response):
        pattern = r'!\[.*?\]\((.*?)\)'
        match = re.search(pattern, wolfram_response)
        if match:
            url = match.group(1)
            image = base64.b64encode(requests.get(url).content).decode("utf-8")
            return "data:image/jpeg;base64," + image
        else:
            return None

    def solve(self, chat, messages, language=None):
        question = chat[ChatColumn.QUESTION]
        learner_mode = chat[ChatColumn.LEARNER_MODE]
        wolfram_query = chat[ChatColumn.WOLFRAM_QUERY]
        chat_id = chat["id"]
        try:
            extracted_response = ""
            if wolfram_query:
                wolfram_alpha_response = self._query_wolfram_alpha(wolfram_query)
                extracted_response = ""
                if wolfram_alpha_response:
                    extracted_response = self._extract_wolfram_alpha_response(
                        wolfram_alpha_response, question
                    )
                    extracted_response = replace_wolfram_image(extracted_response)
                    column = {ChatColumn.WOLFRAM_ANSWER: extracted_response,
                              ChatColumn.WOLFRAM_IMAGE: self._extract_wolfram_image(extracted_response)}
                    self.supabase.update_columns_by_primary_id(
                        table="chats", primary_id=chat_id, columns=column
                    )
            question_context = f"""
            <question>{question}</question>
            <text_prompt>{chat[ChatColumn.TEXT_PROMPT]}</text_prompt>
            <image_content>{chat[ChatColumn.IMAGE_CONTENT]}</image_content>
            """
            user_prompt = get_user_prompt_for_solve(
                question_context, extracted_response, learner_mode
            )
            system_prompt = SYSTEM_PROMPT
            if language:
                system_prompt += LANGUAGE_PROMPT.format(language=language)

            messages.extend(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ]
            )
            return self.query(messages)
        except Exception as e:
            print(e)
            raise Exception(e)

    @timer(log_level=TimerLogLevel.STANDARD)
    def _query_wolfram_alpha(self, wolfram_query):
        params = {
            "input": wolfram_query,
            "appid": self.wolf_api_key,
            "output": "JSON",
        }
        try:
            response = requests.get(self.wolfram_url, params=params)
            response_data = response.json()
            query_result = response_data["queryresult"]
            if (
                query_result.get("success")
                and "pods" in query_result
                and query_result["pods"]
            ):
                return query_result["pods"]
            else:
                return None
        except KeyError as e:
            error_message = f"KeyError: The key {e} is missing in the response."
            logging.error(error_message)
            return None
        except IndexError as e:
            logging.error(e)
            return None

    @timer(log_level=TimerLogLevel.BASIC)
    def _extract_wolfram_alpha_response(self, wa_response, question):
        session = self._cur_openai_client()
        response = session.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            temperature=0.1,
            messages=[
                {"role": "system", "content": WOLFRAM_ALPHA_SUMMARIZE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": WOLFRAM_ALPHA_SUMMARIZE_TEMPLATE.format(
                        response=wa_response, context=question
                    ),
                },
            ],
            stop=["###SYSTEM_PROMPT"],
        )
        return response.choices[0].message.content
