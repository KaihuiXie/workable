from openai import OpenAI

from src.math_agent.prompts import IMAGE_READING_PROMPT, HELPER_PROMPT, LEARNING_PROMPT


class MathAgent:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def _compose_image_content(self, image_base64_str, text_prompt):
        return [
            {"type": "text", "text": text_prompt},
            {
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{image_base64_str}",
            },
        ]

    def query_vision(self, image_base64_str):
        content = self._compose_image_content(image_base64_str, IMAGE_READING_PROMPT)
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{"role": "user", "content": content}],
            max_tokens=1000,
        )
        return response.choices[0].message.content

    def query(self, messages):
        stream = self.client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stream=True,
        )
        return stream

    def helper(self, messages):
        messages.append({"role": "user", "content": HELPER_PROMPT})
        return self.query(messages)

    def learner(self, messages):
        messages.append({"role": "user", "content": LEARNING_PROMPT})
        return self.query(messages)
