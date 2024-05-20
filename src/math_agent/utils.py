import base64
import io
import re

import requests


def encode_image_to_base64(image):
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def replace_wolfram_image(markdown_text):
    # Regular expression to find the image URL starting with the specific pattern
    img_url_pattern = r"!\[(.*?)\]\((https://www6b3\.wolframalpha\.com/[^\)]+)\)"
    matches = re.findall(img_url_pattern, markdown_text)

    if not matches:
        print("No image URL found in the markdown text.")
        return markdown_text

    for alt_text, img_url in matches:
        # Fetch the image
        response = requests.get(img_url)
        if response.status_code != 200:
            print(
                f"Failed to fetch the image from {img_url}. Status code: {response.status_code}"
            )
            continue

        # Encode the image as base64
        image_base64 = base64.b64encode(response.content).decode("utf-8")
        image_base64_str = f"data:image/gif;base64,{image_base64}"  # Assuming the image is in GIF format

        # Create the HTML <img> tag
        img_tag = f'<img src="{image_base64_str}" alt="{alt_text}"/>'

        # Replace the original markdown image with the HTML <img> tag
        markdown_text = markdown_text.replace(f"![{alt_text}]({img_url})", img_tag)

    return markdown_text
