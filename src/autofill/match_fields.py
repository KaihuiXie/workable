import json
import openai
from bs4 import BeautifulSoup

from .prompt import get_match_prompt


# Set your OpenAI API key
openai.api_key = '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'  # Replace with your actual OpenAI API key

def extract_form_elements(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find('form')
    if not form:
        return ''
    # Remove script and style elements to reduce size
    for script in form(["script", "style"]):
        script.decompose()
    return str(form)


def parse_html_with_gpt(html, user_info):
    print(html)
    prompt = get_match_prompt(html, user_info)

    try:
        print('parsing html...')
        response = openai.chat.completions.create(
            model="gpt-4o-mini-2024-07-18",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        print('===html parsed')
        # print(response)
        # print(type(response))

        output_text = response.choices[0].message.content
        # print(output_text)
        parsed_fields = json.loads(output_text)
        # print(parsed_fields)
        return parsed_fields
    except Exception as e:
        print(f"Error in GPT API call during field matching: {e}")
        return None


def map_fields_to_user_info(parsed_fields, user_info):
    fields = parsed_fields.get('fields', [])
    mapped_fields = []
    # print(fields)

    for field in fields:
        # print('field: ', field)
        key = field.get('key')
        value = get_value_from_user_info(key, user_info)
        # print(value)
        # print('=========================')
        if value:
            field['value'] = value
            mapped_fields.append(field)
    return mapped_fields


def find_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):
                result = find_key(value, target_key)
                if result is not None:
                    return result
    elif isinstance(data, list):
        for item in data:
            result = find_key(item, target_key)
            if result is not None:
                return result
    return None


def get_value_from_user_info(key, user_info):
    if not key:
        return None
    keys = key.split('.')
    # print("key: ", key)
    # print("keys: ", keys)
    data = user_info
    for k in keys:
        # print("k: ", k)
        if isinstance(data, list):
            # For lists, we might need more logic to select the appropriate item
            data = data[0]
        if isinstance(data, dict):
            data = find_key(data, k)
        else:
            return None
    return data