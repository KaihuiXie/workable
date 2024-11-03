from .promtps.parse import parse_prompt, parse_sample

def get_prompt(simplified_html=None, user_info=None):
    prompt = parse_prompt.format(simplified_html=simplified_html, user_info=user_info) + parse_sample
    return prompt


if __name__ == '__main__':
    print(get_prompt(simplified_html='html', user_info='ifo'))