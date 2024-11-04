import json
import openai
import fitz  # PyMuPDF for PDF files
import docx  # python-docx for Word files
import os

from .prompt import get_resume_prompt


def convert_file_to_text(file_path):
    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension == '.pdf':
        return convert_pdf_to_text(file_path)
    elif file_extension == '.docx':
        return convert_word_to_text(file_path)
    elif file_extension == '.txt':
        return convert_txt_to_text(file_path)
    else:
        raise ValueError("Unsupported file format. Please use PDF, DOCX, or TXT.")

def convert_pdf_to_text(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def convert_word_to_text(word_path):
    doc = docx.Document(word_path)
    text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
    return text

def convert_txt_to_text(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as txt_file:
        return txt_file.read()

def parse_resume(resume_path):
    resume = convert_file_to_text(resume_path)
    prompt = get_resume_prompt(resume)

    try:
        print('parsing resume...')
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )
        print('====resume parsed')
        # print(response)
        # print(type(response))

        output_text = response.choices[0].message.content
        print(output_text)
        parsed_fields = json.loads(output_text)
        # print(parsed_fields)
        return parsed_fields
    except Exception as e:
        print(f"Error in GPT API call during resume parsing: {e}")
        return None


def test():
    file_path = 'data/CV_Kaihui_Xie.pdf'  # Replace with your file path
    #text_content = convert_file_to_text(file_path)
    #print(text_content)  # Output the extracted text

    print(parse_resume(file_path))