import logging
import time

import requests
from openai import OpenAI

from src.math_agent.prompts import (
    HELPER_PROMPT,
    IMAGE_READING_PROMPT,
    LANGUGAE_PROMPT,
    LATEX_PROMPT,
    LEARNING_PROMPT,
    QUESTION_CONTEXT_PROMPT,
    SYSTEM_PROMPT,
    WOLFRAM_ALPHA_PROMPT,
    WOLFRAM_ALPHA_SUMMARIZE_SYSTEM_PROMPT,
    WOLFRAM_ALPHA_SUMMARIZE_TEMPLATE,
)
from src.math_agent.utils import replace_wolfram_image

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
                "image_url": {"url": f"data:image/jpeg;base64,{image_base64_str}"},
            },
        ]

    def query_vision(self, image_base64_str, additional_prompt):
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

    def query(self, messages):
        start_time = time.time()  # Record the start time
        session = self._cur_openai_client()
        stream = session.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stop=["###SYSTEM_PROMPT"],
            stream=True,
        )
        end_time = time.time()  # Record the end time
        time_taken = end_time - start_time  # Calculate the time taken
        # Log or store the time taken
        print("OpenAI Query before first reponse received:", time_taken)

        return stream

    def helper(self, question, messages, language):
        return self._solve(question, HELPER_PROMPT, messages, language)

    def learner(self, question, messages, language):
        return self._solve(question, LEARNING_PROMPT, messages, language)

    def _generate_wolfram_query(self, question):
        start_time = time.time()  # Record the start time
        session = self._cur_openai_client()
        response = session.chat.completions.create(
            model="gpt-4o",
            temperature=0.1,
            messages=[
                {"role": "user", "content": WOLFRAM_ALPHA_PROMPT.format(question)}
            ],
        )
        end_time = time.time()
        print("generate wolfram query took:", end_time - start_time)
        response_str = response.choices[0].message.content
        return response_str

    def _solve(self, question, mode_prompt, messages, language=None):
        try:
            wolfram_alpha_response = self._query_wolfram_alpha(question)

            start_time = time.time()

            extracted_response = ""
            if wolfram_alpha_response:
                extracted_response = self._extract_wolfram_alpha_response(
                    wolfram_alpha_response, question
                )
                extracted_response = replace_wolfram_image(extracted_response)
                print(extracted_response)

            end_time1 = time.time()
            print("extract wolfram took:", end_time1 - start_time)

            text_prompt = (mode_prompt).format(
                context=question, reference=extracted_response
            )

            system_prompt = SYSTEM_PROMPT
            if language:
                system_prompt += LANGUGAE_PROMPT.format(language=language)

            messages.extend(
                [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_prompt},
                ]
            )
            return self.query(messages)
        except Exception as e:
            print(e)
            raise Exception(e)

    def _query_wolfram_alpha(self, query):
        url = "http://api.wolframalpha.com/v2/query"
        generated_wolfram = self._generate_wolfram_query(query)
        params = {
            "input": generated_wolfram,
            "appid": self.wolf_api_key,
            "output": "JSON",
        }
        print(generated_wolfram)
        print("==========================")
        start_time = time.time()  # Record the start time
        try:
            response = requests.get(url, params=params)
            response_data = response.json()
            end_time = time.time()
            print("query wolfram took:", end_time - start_time)
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
