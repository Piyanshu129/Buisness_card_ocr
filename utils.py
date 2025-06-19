from PIL import Image, ImageEnhance
from io import BytesIO
import re

def preprocess_image(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2.0)
    return enhanced_image.convert("RGB")


# image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
#     if max(image.size) > 1000:
#         image.thumbnail((1000, 1000))  # Resize in-place
#     return image
def is_low_quality_text(lines):
    if len(lines) < 3: return True
    joined_text = " ".join(lines)
    email_found = bool(re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", joined_text))
    phone_found = bool(re.search(r"\+?\d[\d\- ]{7,}\d", joined_text))
    noise_ratio = sum(1 for c in joined_text if not c.isalnum() and c not in "@.:-, ") / max(len(joined_text), 1)
    return not email_found or not phone_found or noise_ratio > 0.5
