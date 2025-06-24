import pytesseract
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
import uvicorn
from PIL import Image
import io
import re # Import the regular expressions library
from pydantic import BaseModel
from typing import Optional

# --- Pydantic Model for Structured Data ---
# This defines the structure of our JSON output.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# 'Optional' means the field might not be found.
class PANCardDetails(BaseModel):
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None
    # We can add father's name and other fields later

# Initialize our FastAPI app
app = FastAPI(title="PAN Card OCR Extractor")

def preprocess_image(image_bytes: bytes):
    """
    Takes image bytes, converts to grayscale.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_image

def extract_text(image_bytes: bytes) -> str:
    """
    Takes image bytes, preprocesses, and extracts text.
    """
    processed_image = preprocess_image(image_bytes)
    raw_text = pytesseract.image_to_string(processed_image)
    return raw_text

# --- NEW PARSING FUNCTION ---
def parse_pan_details(raw_text: str) -> PANCardDetails:
    """
    Parses the raw OCR text to find PAN number, DOB, and name.
    """
    details = PANCardDetails()

    # 1. Regex for PAN Number
    # Format: 5 uppercase letters, 4 digits, 1 uppercase letter.
    pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    pan_match = re.search(pan_regex, raw_text)
    if pan_match:
        details.pan_number = pan_match.group(0)

    # 2. Regex for Date of Birth
    # Format: dd/mm/yyyy
    dob_regex = r"\d{2}/\d{2}/\d{4}"
    dob_match = re.search(dob_regex, raw_text)
    if dob_match:
        details.date_of_birth = dob_match.group(0)

    # 3. Rule-based extraction for Name
    # This is more complex. PAN cards often have "Name" on one line
    # and the actual name on the next. We will look for lines that are
    # likely to be names (e.g., all uppercase, multiple words).
    lines = raw_text.split('\n')
    for i, line in enumerate(lines):
        # A simple heuristic: The line after "Name" is often the name.
        # This is a basic approach and can be improved.
        if "Name" in line and i + 1 < len(lines):
             # Check if the next line looks like a name (e.g., is uppercase)
            next_line = lines[i+1].strip()
            if next_line and next_line.isupper():
                details.name = next_line
                break # Stop after finding the first likely name

    return details

@app.post("/ocr/pan_card", response_model=PANCardDetails)
async def perform_pan_ocr(image: UploadFile = File(...)):
    """
    API endpoint to upload a PAN card image and get structured details.
    """
    image_bytes = await image.read()
    
    # Step 1: Extract raw text
    raw_text = extract_text(image_bytes)
    
    # Step 2: Parse the raw text to get structured data
    structured_data = parse_pan_details(raw_text)
    
    return structured_data

# Main block to run the app
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)











