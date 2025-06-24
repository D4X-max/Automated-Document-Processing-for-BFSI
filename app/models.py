from pydantic import BaseModel
from typing import Optional
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class PANCardDetails(BaseModel):
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None
