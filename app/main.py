from fastapi import FastAPI, File, UploadFile
import uvicorn
import pytesseract
from app.models import PANCardDetails
from app.services.ocr_service import extract_text
from app.services.pan_parser import parse_pan_details
from app.models import PANCardDetails, AadhaarCardDetails, UnifiedProcessingResult
from app.services.ocr_service import extract_text
from app.services.pan_parser import parse_pan_details
from app.services.aadhaar_parser import parse_aadhaar_details
from app.services.document_classifier import classify_document, DocumentType
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from app.database import pan_collection, aadhaar_collection

app = FastAPI(title="Document Processing API")

@app.post("/v1/process_document", response_model=UnifiedProcessingResult, tags=["V1 - Core Processing"])
async def process_document_endpoint(image: UploadFile = File(...)):
    # ... (steps 1 and 2 for OCR and classification remain the same) ...
    image_bytes = await image.read()
    raw_text = extract_text(image_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text.")
    doc_type = classify_document(raw_text)

    # Step 3: Route, Parse, and VALIDATE
    if doc_type == DocumentType.PAN_CARD:
        data = parse_pan_details(raw_text)
        is_duplicate = False
        # Check if the PAN number exists and was parsed correctly
        if data.pan_number:
            if pan_collection.find_one({"pan_number": data.pan_number}):
                is_duplicate = True
            else:
                # Save to DB if not a duplicate. We convert Pydantic model to dict.
                pan_collection.insert_one(data.dict())
        
        return UnifiedProcessingResult(
            document_type=doc_type.value,
            is_successfully_parsed=True,
            is_duplicate=is_duplicate,
            data=data
        )
    elif doc_type == DocumentType.AADHAAR_CARD:
        data = parse_aadhaar_details(raw_text)
        is_duplicate = False
        # Check if Aadhaar number exists and was parsed correctly
        if data.aadhaar_number:
            if aadhaar_collection.find_one({"aadhaar_number": data.aadhaar_number}):
                is_duplicate = True
            else:
                aadhaar_collection.insert_one(data.dict())

        return UnifiedProcessingResult(
            document_type=doc_type.value,
            is_successfully_parsed=True,
            is_duplicate=is_duplicate,
            data=data
        )
    else:
        return UnifiedProcessingResult(
            document_type=DocumentType.UNKNOWN.value,
            is_successfully_parsed=False,
            is_duplicate=None,
            data=None
        )

@app.post("/ocr/pan_card", response_model=PANCardDetails, tags=["OCR - KYC Documents"])
async def ocr_pan_card_endpoint(image: UploadFile = File(...)):
    """
    Extracts structured data from a PAN Card image.
    """
    image_bytes = await image.read()
    raw_text = extract_text(image_bytes)
    structured_data = parse_pan_details(raw_text)
    return structured_data

@app.post("/ocr/aadhaar_card", response_model=AadhaarCardDetails, tags=["OCR - KYC Documents"])
async def ocr_aadhaar_card_endpoint(image: UploadFile = File(...)):
    """
    Extracts structured data from an Aadhaar Card image.
    """
    image_bytes = await image.read()
    # Step 1: Reuse our generic OCR service
    raw_text = extract_text(image_bytes)
    # Step 2: Use our new, specific Aadhaar parser
    structured_data = parse_aadhaar_details(raw_text)
    return structured_data

# This part is now optional, as we'll run the app with a command.
# But it's good practice to keep it for direct execution.
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
