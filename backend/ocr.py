#text extraction from facebook memes
from PIL import Image,ImageOps
import pytesseract

#This function uses the pytesseract library to extract the text from the image.
def extract_text(image_path: str)-> str:
    #open the image
    img = Image.open(image_path)

     # 2. IMPROVEMENT: Convert to Grayscale & Increase Contrast
    # This helps Tesseract distinguish Sinhala letters from colorful meme backgrounds
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    
    #Page segmentation mode(PSM)
    # 3. IMPROVEMENT: Custom Tesseract Config for Mixed English-Sinhala Text
    #PSM 3 is 'Fully automatic page segmentation' - best for memes with scattered text
    custom_config = r'--psm 3 --oem 3'

    #Extract text using both English and Sinhala trained data 
    text = pytesseract.image_to_string(img,lang="eng+sin" , config=custom_config)
    
    #Clean whitespace and unwanted characters
    cleaned_text = text.strip().replace('|','') #Tesseract often misidentifies lines as '|

    return cleaned_text


   