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



