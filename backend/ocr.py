
from PIL import Image
import pytesseract

def extract_text(image_path: str)-> str:
    img = Image.open(image_path).convert("RGB")
    text = pytesseract.image_to_string(img,lang="eng+sin")
    return text.strip()  