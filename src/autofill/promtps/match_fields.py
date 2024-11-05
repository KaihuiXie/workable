match_prompt = f"""
You are an AI assistant that extracts form field details from HTML job application forms.

Given the following HTML form:

```
{{html}}
```

Identify all input fields that a user needs to fill in. For each field, provide:
- "label": The associated label text (e.g., 'First Name', 'Email'). If not available, use the 'placeholder' attribute.
- "selector": A CSS selector that uniquely identifies the field (e.g., 'input#first_name', 'input[name="email"]').
- "required": Whether the field is required (True/False).
- "key": A generalized key mapping to user info (e.g., 'first_name', 'email').

I will give you the user's information (user_info) later. 
try to align "key" with the user information json file's keys when you are figuring out the fields. Also make sure you don't force match irrelevant keys. 
1. If there is no obvious match, like if the blank ask why apply, don't match it with cover letter.
2. If a key is in a nested json, return only the name of the key and don't include parent nodes. 
3. Sometimes, in blanks with options, the values from user_info that you need to assign to the fields are not exactly the same as the options in the field. you might get the value first and then think of the most close meaning option to the value. return that option as value.
4. remember don't make up any answers.
5. If there is a blank for current company, find the company name when the date as present or use value 'None' if there aren't any. 

Ensure the CSS selector is accurate and can be used in document.querySelector().

also here is the user's information (user_info). 
```{{user_info}}```
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

