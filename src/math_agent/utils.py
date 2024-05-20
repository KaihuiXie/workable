import base64
import io
import re

import requests


def encode_image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def shorten_url(url):
    api_url = f"http://tinyurl.com/api-create.php?url={url}"
    response = requests.get(api_url)
    if response.status_code != 200:
        print(
            f"Failed to shorten the image from {url}. Status code: {response.status_code}"
        )

    return response.text


def replace_wolfram_image(markdown_text):
    # Regular expression to find the image URL starting with the specific pattern
    img_url_pattern = r"!\[(.*?)\]\((https://www6b3\.wolframalpha\.com/[^\)]+)\)"
    matches = re.findall(img_url_pattern, markdown_text)

    if not matches:
        print("No image URL found in the markdown text.")
        return markdown_text

    for alt_text, img_url in matches:
        short_url = shorten_url(img_url)

        # Replace the original markdown image with the HTML <img> tag
        markdown_text = markdown_text.replace(f"{img_url}", short_url)

    return markdown_text
