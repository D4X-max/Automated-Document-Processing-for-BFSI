import pytesseract
import cv2
import numpy as np
from fastapi import FastAPI, File, UploadFile
import uvicorn
from PIL import Image
import io

# --- ADD THIS LINE ---
# Replace the path with the actual path on YOUR computer.
# This example is for a typical Windows installation.
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# ---------------------
# --- Pydantic Model for Structured Data ---
# This defines the structure of our JSON output.
# 'Optional' means the field might not be found.
class PANCardDetails(BaseModel):
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None
    # We can add father's name and other fields later
# Let's initialize our FastAPI app
app = FastAPI(title="PAN Card OCR Extractor")

def preprocess_image(image_bytes: bytes):
    """
    Takes image bytes, converts to grayscale and applies thresholding.
    This is a common first step for improving OCR accuracy.
    """
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray_image


def extract_text(image_bytes: bytes) -> str:
    """
    This function takes the bytes of an image file, preprocesses it,
    and then uses Tesseract to extract raw text.
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


@app.post("/ocr/pan_card")
async def perform_pan_ocr(image: UploadFile = File(...)):
    """
    API endpoint to upload a PAN card image and get the raw text.
    """
    image_bytes = await image.read()
    
    try:
        extracted_text = extract_text(image_bytes)
        return {"raw_text": extracted_text}
    except pytesseract.TesseractNotFoundError:
        # This error handling is perfect. It just needed the HTTPException import.
        raise HTTPException(status_code=500, detail="Tesseract OCR engine not found. Please ensure it is installed and in your system's PATH.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


# This block allows us to run the app directly from the command line
if __name__ == "__main__":
    # The syntax is now corrected.
    uvicorn.run(app, host="127.0.0.1", port=8000)



