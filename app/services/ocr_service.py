import pytesseract
import cv2
import numpy as np
def preprocess_image(image_bytes: bytes):
    """
    Takes image bytes and applies a series of preprocessing steps to improve OCR accuracy.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Convert to grayscale
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)


    return gray_image

def extract_text(image_bytes: bytes) -> str:
    """
    Takes image bytes, preprocesses, and extracts text using Tesseract
    with an improved configuration.
    """
    processed_image = preprocess_image(image_bytes)
    
    # Configure Tesseract with OEM and PSM modes for better accuracy
    # --oem 3: Use the LSTM engine (modern and more accurate).
    # --psm 6: Assume the image is a single uniform block of text (good for ID cards).
    custom_config = r'--oem 3 --psm 6'
    
    raw_text = pytesseract.image_to_string(processed_image, config=custom_config)
    
    return raw_text
