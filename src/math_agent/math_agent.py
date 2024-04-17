from openai import OpenAI
import requests
import logging

from src.math_agent.prompts import (
    IMAGE_READING_PROMPT,
    HELPER_PROMPT,
    LEARNING_PROMPT,
    WOLFRAM_ALPHA_PROMPT,
    WOLFRAM_ALPHA_SUMMARIZE_TEMPLATE,
    WOLFRAM_ALPHA_SUMMARIZE_SYSTEM_PROMPT,
    SYSTEM_PROMPT,
)

# Configure logging
logging.basicConfig(level=logging.INFO)


class MathAgent:
    def __init__(self, openai_api_keys: str, wolf_api_key):
        self.open_ai_keys = [s.strip() for s in openai_api_keys.split(",")]
        self.wolf_api_key = wolf_api_key

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
                "image_url": f"data:image/jpeg;base64,{image_base64_str}",
            },
        ]

    def query_vision(self, image_base64_str):
        session = self._cur_openai_client()
        content = self._compose_image_content(image_base64_str, IMAGE_READING_PROMPT)
        response = session.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": content}],
            max_tokens=1000,
        )
        return response.choices[0].message.content

    def query(self, messages):
        session = self._cur_openai_client()
        stream = session.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stream=True,
        )
        return stream

    def helper(self, question, messages):
        return self._solve(question, HELPER_PROMPT, messages)

    def learner(self, question, messages):
        return self._solve(question, LEARNING_PROMPT, messages)

    def _generate_wolfram_query(self, question):
        session = self._cur_openai_client()
        response = session.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "user", "content": WOLFRAM_ALPHA_PROMPT.format(question)}
            ],
        )
        response_str = response.choices[0].message.content
        return response_str

    def _solve(self, question, mode_prompt, messages):
        wolfram_alpha_response = self._query_wolfram_alpha(question)
        extracted_response = ""
        if wolfram_alpha_response:
            extracted_response = self._extract_wolfram_alpha_response(
                wolfram_alpha_response, question
            )

        text_prompt = (mode_prompt).format(
            question=question, reference=extracted_response
        )

        messages.extend(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text_prompt},
            ]
        )
        return self.query(messages)

    def _query_wolfram_alpha(self, query):
        url = "http://api.wolframalpha.com/v2/query"
        params = {
            "input": self._generate_wolfram_query(query),
            "appid": self.wolf_api_key,
            "output": "JSON",
        }
        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            # st.sidebar.write(response_data)
            if not response_data["queryresult"]["success"]:
                return None
            return response_data
        except KeyError as e:
            error_message = f"KeyError: The key {e} is missing in the response."
            logging.error(error_message)
            return None
        except IndexError as e:
            logging.error(error_message)
            return None

    def _extract_wolfram_alpha_response(self, wa_response, question):
        session = self._cur_openai_client()
        response = session.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": WOLFRAM_ALPHA_SUMMARIZE_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": WOLFRAM_ALPHA_SUMMARIZE_TEMPLATE.format(
                        response=wa_response, question=question
                    ),
                },
            ],
        )
        return response.choices[0].message.content
