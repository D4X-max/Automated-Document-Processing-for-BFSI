import re
from enum import Enum

class DocumentType(Enum):
    PAN_CARD = "PAN_CARD"
    AADHAAR_CARD = "AADHAAR_CARD"
    UNKNOWN = "UNKNOWN"

def classify_document(text: str) -> DocumentType:
    """
    Classifies a document based on key patterns and identifiers in the text.
    """
    text = text.upper()

    # Clean text for pattern matching
    text_no_spaces = text.replace(" ", "").replace("\n", "")

    # --------------------
    # Aadhaar Detection
    # --------------------
    aadhaar_keywords = ['AADHAAR', 'UNIQUE IDENTIFICATION', 'VID', 'GOVERNMENT OF INDIA']
    aadhaar_number_pattern = re.compile(r'\b\d{4}\s\d{4}\s\d{4}\b')  # 12-digit format with spaces
    aadhaar_number_compact_pattern = re.compile(r'\b\d{12}\b')  # in case OCR removes spaces

    if (
        any(keyword in text for keyword in aadhaar_keywords) or
        aadhaar_number_pattern.search(text) or
        aadhaar_number_compact_pattern.search(text_no_spaces)
    ):
        return DocumentType.AADHAAR_CARD

    # --------------------
    # PAN Detection
    # --------------------
    pan_keywords = ['INCOME TAX DEPARTMENT', 'PERMANENT ACCOUNT NUMBER', 'GOVT. OF INDIA', 'INDIA', 'INCOMETAX']
    pan_number_pattern = re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b')

    # Try to find a valid PAN format
    if pan_number_pattern.search(text_no_spaces):
        return DocumentType.PAN_CARD

    # Fallback on PAN-related keywords
    if any(keyword in text for keyword in pan_keywords):
        # If keywords match but PAN pattern fails, still likely to be PAN
        return DocumentType.PAN_CARD

    # --------------------
    # Default: Unknown
    # --------------------
    return DocumentType.UNKNOWN

