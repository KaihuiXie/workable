import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import openai
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
CORS(app)

# Load user information
with open('data/user_info.json', 'r') as f:
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
    parsed_fields = parse_html_with_gpt(simplified_html, user_info)
    #json.dump(parsed_fields, open('parsed_fields.json', 'w'))
    print('4444')
    if not parsed_fields:
        return jsonify({'error': 'Failed to parse fields from HTML.'}), 500
    mapped_fields = map_fields_to_user_info(parsed_fields, user_info)
    return jsonify({'fields': mapped_fields})

@app.route('/get_resume', methods=['GET'])
def get_resume():
    try:
        return send_file(find_key(user_info, 'resume'), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def extract_form_elements(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    form = soup.find('form')
    if not form:
        return ''
    # Remove script and style elements to reduce size
    for script in form(["script", "style"]):
        script.decompose()
    return str(form)

def parse_html_with_gpt(simplified_html, user_info):
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
        
        also here is the user's information. 
        ```{user_info}```
        try to align "key" with the user information json file's keys when you are figuring out the fields. Also make sure you don't force match irrelevant keys.
        
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
            temperature=0.2
        )
        print('parsed')
        #print(response)
        #print(type(response))

        output_text = response.choices[0].message.content
        #print(output_text)
        parsed_fields = json.loads(output_text)
        #print(parsed_fields)
        return parsed_fields
    except Exception as e:
        print(f"Error in GPT API call: {e}")
        return None

def map_fields_to_user_info(parsed_fields, user_info):
    fields = parsed_fields.get('fields', [])
    mapped_fields = []
    #print(fields)

    for field in fields:
        #print('field: ', field)
        key = field.get('key')
        value = get_value_from_user_info(key, user_info)
        #print(value)
        #print('=========================')
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
    #print("key: ", key)
    #print("keys: ", keys)
    data = user_info
    for k in keys:
        #print("k: ", k)
        if isinstance(data, list):
            # For lists, we might need more logic to select the appropriate item
            data = data[0]
        if isinstance(data, dict):
            data = find_key(data, k)
        else:
            return None
    return data

if __name__ == '__main__':
    # Set host to '0.0.0.0' if you want it accessible over the network
    app.run(host='0.0.0.0', port=5000, debug=True)
