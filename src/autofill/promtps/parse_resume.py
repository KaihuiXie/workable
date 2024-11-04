resume_prompt = """
You are an AI assistant that will convert a resume into a structured JSON format. The resume text may contain inconsistent line breaks, extra whitespace, or other formatting artifacts from conversion. Clean up the text as needed and organize it according to the specified JSON schema.
Given the text below, extract the information and organize it according to the specified JSON schema. Ensure each section and field is accurately captured, preserving details and providing null values for missing fields. Make sure to follow these instructions:

Name: Separate first_name, middle_name, last_name, and include a title field if available (e.g., Mr., Ms., Dr.).
Phone Number: Convert to numeric-only format, including only digits. If the phone number has 10 digits, add the country code as "+1" (US). Otherwise, include the detected country code.
Contact Information: Ensure the output includes phone, email, location, LinkedIn, GitHub, website (personal website), and summary fields.
Education: Separate GPA into two fields, gpa_score and gpa_scale. For each date, use day, month, and year format separately. Include a details field that contains relevant_courses and any additional details if provided.
Location: Structure all locations to follow a detailed address format, breaking down as:
["address_1": Primary address line.
"address_2": Secondary address line (if applicable).
"city": City name.
"state": State or region name.
"postal_code": Postal code.
"country": Country name.]
Date Formatting: All dates (including those from education and other experience) should be separated into day, month, and year fields. Sometimes users only provide month and year, beware of that and give null to day if it appears to have only month and year like 08/2024 or Aug 2024.
For the latest employment information, beware that users are still in a company and you should keep that information.  
Use the following schema:

{
  "title": "Title",
  "first_name": "First Name",
  "middle_name": "Middle Name",
  "last_name": "Last Name",
  "phone": {
    "country_code": "Country Code",
    "number": "Numeric Phone Number"
  },
  "email": "Email Address",
  "location": {
    "address_1": "Primary Address Line",
    "address_2": "Secondary Address Line",
    "city": "City",
    "state": "State or Region",
    "postal_code": "Postal Code",
    "country": "Country"
  },
  "linkedin": "LinkedIn URL",
  "github": "GitHub URL",
  "website": "Personal Website URL",
  "summary": "Brief summary or objective if available",
  "education": [
    {
      "school": "School Name",
      "location": {
        "address_1": "Primary Address Line",
        "address_2": "Secondary Address Line",
        "city": "City",
        "state": "State or Region",
        "postal_code": "Postal Code",
        "country": "Country"
      },
      "degree": "Degree",
      "gpa": {
        "gpa_score": "GPA Score",
        "gpa_scale": "GPA Scale"
      },
      "start_date": {
        "day": "Start Day",
        "month": "Start Month",
        "year": "Start Year"
      },
      "end_date": {
        "day": "End Day",
        "month": "End Month",
        "year": "End Year"
      },
      "details": {
        "relevant_courses": [
          "Course1",
          "Course2",
          ...
        ],
        "other_details": "Additional details if available"
      }
    },
    ...
  ],
  "skills": {
    "programming_languages": [
      "Language1",
      "Language2",
      ...
    ],
    "web_development": [
      "Framework1",
      "Framework2",
      ...
    ],
    "machine_learning_frameworks": [
      "Framework1",
      "Framework2",
      ...
    ],
    "databases": [
      "Database1",
      "Database2",
      ...
    ],
    "data_analysis_tools": [
      "Tool1",
      "Tool2",
      ...
    ],
    "version_control": [
      "Tool1",
      "Tool2",
      ...
    ],
    "languages": [
      "Language1",
      "Language2",
      ...
    ]
  },
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "department": "Department Name",
      "location": {
        "address_1": "Primary Address Line",
        "address_2": "Secondary Address Line",
        "city": "City",
        "state": "State or Region",
        "postal_code": "Postal Code",
        "country": "Country"
      },
      "start_date": {
        "day": "Start Day",
        "month": "Start Month",
        "year": "Start Year"
      },
      "end_date": {
        "day": "End Day",
        "month": "End Month",
        "year": "End Year"
      },
      "responsibilities": [
        "Responsibility1",
        "Responsibility2",
        ...
      ]
    },
    ...
  ],
  "projects": [
    {
      "title": "Project Title",
      "course": "Course Name or Type",
      "school": "School or Organization",
      "location": {
        "address_1": "Primary Address Line",
        "address_2": "Secondary Address Line",
        "city": "City",
        "state": "State or Region",
        "postal_code": "Postal Code",
        "country": "Country"
      },
      "start_date": {
        "day": "Start Day",
        "month": "Start Month",
        "year": "Start Year"
      },
      "end_date": {
        "day": "End Day",
        "month": "End Month",
        "year": "End Year"
      },
      "details": [
        "Detail1",
        "Detail2",
        ...
      ]
    },
    ...
  ]
}
"""
resume_input_prompt = """Now, parse the resume text below into this JSON structure (remember your output should only has json without the markdown format):

{resume}
"""
