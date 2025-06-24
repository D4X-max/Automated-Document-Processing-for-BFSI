from fastapi import FastAPI, File, UploadFile
import uvicorn
import pytesseract
from app.models import PANCardDetails
from app.services.ocr_service import extract_text
from app.services.pan_parser import parse_pan_details
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

app = FastAPI(title="Document Processing API")

@app.post("/ocr/pan_card", response_model=PANCardDetails, tags=["OCR - KYC Documents"])
async def ocr_pan_card_endpoint(image: UploadFile = File(...)):
    """
    Extracts structured data from a PAN Card image.
    """
    image_bytes = await image.read()
    raw_text = extract_text(image_bytes)
    structured_data = parse_pan_details(raw_text)
    return structured_data

# This part is now optional, as we'll run the app with a command.
# But it's good practice to keep it for direct execution.
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
