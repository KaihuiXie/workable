match_prompt = f"""
        You are an AI assistant that extracts form field details from HTML job application forms.

        Given the following HTML form:

        ```
        {{simplified_html}}
        ```

        Identify all input fields that a user needs to fill in. For each field, provide:
        - "label": The associated label text (e.g., 'First Name', 'Email'). If not available, use the 'placeholder' attribute.
        - "selector": A CSS selector that uniquely identifies the field (e.g., 'input#first_name', 'input[name="email"]').
        - "required": Whether the field is required (True/False).
        - "key": A generalized key mapping to user info (e.g., 'first_name', 'email').

        also here is the user's information (user_info). 
        ```{{user_info}}```
        try to align "key" with the user information json file's keys when you are figuring out the fields. Also make sure you don't force match irrelevant keys. 
        If there is no obvious match, like if the blank ask why apply, don't match it with cover letter.
        If it's "True" in user_info, output Yes; if it's "False" in user_info, output No.
        If a key is in a nested json, return only the name of the key and don't include parent nodes. 

        Ensure the CSS selector is accurate and can be used in document.querySelector().
"""
match_output_sample = """
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

