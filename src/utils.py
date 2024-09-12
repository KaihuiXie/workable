import base64
import logging
import json
import time
from io import BytesIO

from PIL import Image
from pillow_heif import register_heif_opener

from common.constants import MAX_MESSAGE_SIZE
from common.decorators import TimerLogLevel, timer

register_heif_opener()
# Configure logging
logging.basicConfig(level=logging.INFO)


def convert_to_jpeg(image_bytes, scale_factor=1.0):
    """
    Converts an image file to JPEG format and downsample it.
    """
    # Open the image file and convert to RGB
    image = Image.open(BytesIO(image_bytes))
    image = image.convert("RGB")

    # Resample the image if scale_factor is not 1
    if scale_factor != 1.0:
        new_size = (int(image.width * scale_factor), int(image.height * scale_factor))
        image = image.resize(new_size, Image.ANTIALIAS)

    # Convert the image back to bytes
    output = BytesIO()
    image.save(output, format="jpeg")
    shrunk_image_bytes = output.getvalue()
    return shrunk_image_bytes


def bytes_to_base64(bytes):
    """
    Converts bytes contained in bytes object to a Base64-encoded string.
    """
    # Encode the bytes to Base64 and decode it to a string
    base64_str = base64.b64encode(bytes).decode("utf-8")

    return base64_str


def base64_to_bytes(base64_str):
    """
    Converts a Base64-encoded string back to bytes.
    """
    # Decode the Base64 string to bytes
    original_bytes = base64.b64decode(base64_str)

    return original_bytes


@timer(log_level=TimerLogLevel.BASIC)
def preprocess_image(image_bytes, shrink_ratio=1.0):
    try:
        jpeg_bytes = convert_to_jpeg(image_bytes, shrink_ratio)
        base64_str = bytes_to_base64(jpeg_bytes)
        thumbnail_str = generate_thumbnail_string(jpeg_bytes)
        return base64_str, thumbnail_str
    except Exception as e:
        logging.error(e)
        raise Exception(f"An error occurred preprocessing image: {e}")


def generate_thumbnail_string(image_bytes, thumbnail_size=(128, 128)):
    image = Image.open(BytesIO(image_bytes))
    image.thumbnail(thumbnail_size)
    # Save image to a bytes buffer instead of a file
    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format=image.format)
    # Encode the bytes buffer to Base64 string
    base64_string = bytes_to_base64(img_byte_arr.getvalue())
    return base64_string


def generate_thumbnail_string_from_image_string(image_string):
    image_bytes = base64_to_bytes(image_string)
    return generate_thumbnail_string(image_bytes)


def check_message_size(messages):
    if messages is None:
        return True
    return len(messages) < MAX_MESSAGE_SIZE

def is_valid_jwt_format(token: str) -> bool:
    try:
        # 分割 JWT 为三个部分
        parts = token.split('.')
        if len(parts) != 3:
            return False
        
        # 验证 Header 和 Payload 是否是有效的 Base64 编码的 JSON
        header = base64.urlsafe_b64decode(parts[0] + "==").decode('utf-8')
        payload = base64.urlsafe_b64decode(parts[1] + "==").decode('utf-8')
        
        # 尝试将 Header 和 Payload 解析为 JSON
        json.loads(header)
        json.loads(payload)
        
        # 如果能成功解析，说明格式是有效的
        return True
    except Exception:
        return False