from pydantic import BaseModel
from typing import Optional
import pytesseract
from typing import Optional, Union 

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class PANCardDetails(BaseModel):   # for PAN
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None

class AadhaarCardDetails(BaseModel):   # for Aadhaar
    aadhaar_number: Optional[str] = None
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    
class UnifiedProcessingResult(BaseModel):
    document_type: str
    is_successfully_parsed: bool
    data: Optional[Union[PANCardDetails, AadhaarCardDetails]] = None

