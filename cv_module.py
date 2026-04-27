import pytesseract
from PIL import Image
import numpy as np
import cv2

def extract_text_from_image(image_file, languages='eng+fra+spa+deu+chi_sim') -> str:
    """
    Extracts text from an uploaded image file using Tesseract OCR.
    Uses PIL to read the image and OpenCV for grayscale conversion.
    Supports basic multilingual OCR via the `languages` parameter.
    
    Note: Requires tesseract-ocr and the respective language data files to be installed on the system.
    """
    try:
        # Read the image file using PIL
        if isinstance(image_file, Image.Image):
            img = image_file
        else:
            img = Image.open(image_file)
            
        # Convert to OpenCV format (NumPy array)
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        
        # Convert to grayscale, which often improves OCR accuracy
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Extract text using pytesseract with multilingual support
        text = pytesseract.image_to_string(gray, lang=languages)
        
        return text.strip()
        
    except pytesseract.TesseractNotFoundError:
        print("Error: Tesseract executable is not installed or not added to your system PATH.")
        return ""
    except Exception as e:
        print(f"Error extracting text from image: {e}")
        return ""
