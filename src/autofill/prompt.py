from .promtps.match_fields import match_prompt, match_output_sample
from .promtps.parse_resume import *

def get_match_prompt(simplified_html=None, user_info=None):
    return match_prompt.format(simplified_html=simplified_html, user_info=user_info) + match_output_sample

def get_resume_prompt(resume):
    return resume_prompt + resume_input_prompt.format(resume=resume)

if __name__ == '__main__':
    print(get_match_prompt(simplified_html='html', user_info='ifo'))