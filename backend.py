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
openai.api_key = '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'  # Replace with your actual OpenAI API key

@app.route('/process_html', methods=['POST'])
def process_html():
    data = request.get_json()
    print('1111')
    html_content = data.get('html', '')
    print('2222')
    simplified_html = extract_form_elements(html_content)
    print('3333')
    parsed_fields = parse_html_with_gpt(simplified_html)
    print('4444')
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
        You are an AI assistant that extracts form field details from HTML job application forms.
        
        Given the following HTML form:
        
        ```html
        {simplified_html}
        ```
        
        Identify all input fields that a user needs to fill in. For each field, provide:
        - "label": The associated label text (e.g., 'First Name', 'Email'). If not available, use the 'placeholder' attribute.
        - "selector": A CSS selector that uniquely identifies the field (e.g., 'input#first_name', 'input[name="email"]').
        - "required": Whether the field is required (True/False).
        - "key": A generalized key mapping to user info (e.g., 'first_name', 'email').
        
        Ensure the CSS selector is accurate and can be used in document.querySelector().
        
        Provide the output in JSON format like (please provide json only, don't generate anything else including text for markdown like "```" sign and json):
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
        print('parsing...')
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.2
        )
        print('parsed')
        #print(response)
        #print(type(response))

        output_text = response.choices[0].message.content
        print(output_text)
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
            # For lists, we might need more logic to select the appropriate item
            data = data[0]
        if isinstance(data, dict) and k in data:
            data = data[k]
        else:
            return None
    return data

if __name__ == '__main__':
    # Set host to '0.0.0.0' if you want it accessible over the network
    app.run(host='0.0.0.0', port=5000, debug=True)
