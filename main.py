# backend.py

import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

# Load user information
with open('user_info.json', 'r') as f:
    user_info = json.load(f)

# Set your OpenAI API key
openai.api_key = 'YOUR_OPENAI_API_KEY'  # Replace with your actual OpenAI API key

@app.route('/process_html', methods=['POST'])
def process_html():
    data = request.get_json()
    html_content = data.get('html', '')
    simplified_html = extract_form_elements(html_content)
    parsed_fields = parse_html_with_gpt(simplified_html)
    if not parsed_fields:
        return jsonify({'error': 'Failed to parse fields from HTML.'}), 500
    mapped_fields = map_fields_to_user_info(parsed_fields, user_info)
    return jsonify({'fields': mapped_fields})

def extract_form_elements(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find('form')
    if not form:
        return ''
    # Remove script and style elements to reduce size
    for script in form(["script", "style"]):
        script.decompose()
    return str(form)

def parse_html_with_gpt(simplified_html):
    prompt = f"""
        Extract form field details from the following HTML form.

        HTML Form Content:
        {simplified_html}

        For each user input field (e.g., <input>, <select>, <textarea>), provide:
        - "label": The associated label text (e.g., 'First Name', 'Email'). If not available, use the 'placeholder' attribute.
        - "selector": A CSS selector that uniquely identifies the field (e.g., 'input#first_name', 'input[name="email"]').
        - "required": Whether the field is required (True/False).
        - "key": A generalized key mapping to user info (e.g., 'first_name', 'email').

        Output the result in JSON format:
        {{
            "fields": [
                {{
                    "label": "First Name",
                    "selector": "input#first_name",
                    "required": true,
                    "key": "first_name"
                }},
                ...
            ]
        }}
        """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.2
        )

        output_text = response['choices'][0]['message']['content']
        parsed_fields = json.loads(output_text)
        return parsed_fields
    except Exception as e:
        print(f"Error in GPT API call: {e}")
        return None

def map_fields_to_user_info(parsed_fields, user_info):
    fields = parsed_fields.get('fields', [])
    mapped_fields = []

    for field in fields:
        key = field.get('key')
        value = get_value_from_user_info(key, user_info)
        if value:
            field['value'] = value
            mapped_fields.append(field)
    return mapped_fields

def get_value_from_user_info(key, user_info):
    keys = key.split('.')
    data = user_info
    for k in keys:
        if isinstance(data, list):
            data = data[0]  # Simplify for example purposes
        data = data.get(k)
        if data is None:
            return None
    return data
