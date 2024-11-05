import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os

from src.autofill import extract_form_elements, parse_html_with_gpt, map_fields_to_user_info, find_key


app = Flask(__name__)
CORS(app)

resume_path = "data/CV_Kaihui_Xie.pdf"

# Load user information
def get_user_info():
    from src.autofill.parse_resume import parse_resume
    if os.path.exists("data/user_info.json"):
        print("existing user_info.json=======")
        with open('data/user_info.json', 'r') as f:
            return json.load(f)
    else:
        print("new user_info.json*******")
        with open('data/user_info.json', 'w') as f:
            info = parse_resume(resume_path)
            f.write(json.dumps(info, indent=4))
            return info


@app.route('/process_html', methods=['POST'])
def process_html():
    user_info = get_user_info()
    data = request.get_json()
    print('1111')
    html_content = data.get('html', '')
    print('2222')
    simplified_html = html_content#extract_form_elements(html_content)
    print('3333')
    parsed_fields = parse_html_with_gpt(simplified_html, user_info)
    #json.dump(parsed_fields, open('parsed_fields.json', 'w'))
    print('4444')
    if not parsed_fields:
        return jsonify({'error': 'Failed to parse fields from HTML.'}), 500
    mapped_fields = map_fields_to_user_info(parsed_fields, user_info)
    print(mapped_fields)
    return jsonify({'fields': mapped_fields})

@app.route('/get_resume', methods=['GET'])
def get_resume():
    try:
        #resume_path = os.path.abspath('CV_Kaihui_Xie.pdf')
        #print(resume_path)
        #print(find_key(user_info, 'resume'))
        return send_file(resume_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Set host to '0.0.0.0' if you want it accessible over the network
    app.run(host='0.0.0.0', port=8080, debug=True)
