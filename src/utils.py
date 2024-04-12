from PIL import Image
from io import BytesIO
import base64
import logging

from pillow_heif import register_heif_opener

register_heif_opener()
# Configure logging
logging.basicConfig(level=logging.info)


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


def preprocess_image(image_bytes, shrink_ratio=1.0):
    try:
        jpeg_bytes = convert_to_jpeg(image_bytes, shrink_ratio)
        return bytes_to_base64(jpeg_bytes)
    except Exception as e:
        logging.error(e)
        raise Exception(f"An error occurred preprocessing image: {e}")
