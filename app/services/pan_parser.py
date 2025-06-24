import re
import spacy
from app.models import PANCardDetails
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Load the spaCy model once here
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    NLP = spacy.load("en_core_web_sm")
    
# --- NEW: Define keywords to exclude from our heuristic search ---
# These are common header texts that are not names.
EXCLUDE_KEYWORDS = {'INCOME', 'TAX', 'DEPARTMENT', 'GOVT', 'INDIA', 'GOVERNMENT', 'PERMANENT', 'ACCOUNT', 'NUMBER'}

def parse_pan_details(raw_text: str) -> PANCardDetails:
    details = PANCardDetails()
    doc = NLP(raw_text)

    # --- Step 1: Regex for fixed-pattern fields ---
    pan_regex = r"[A-Z]{5}[0-9]{4}[A-Z]{1}"
    dob_regex = r"\d{2}/\d{2}/\d{4}"

    pan_match = re.search(pan_regex, raw_text)
    if pan_match:
        details.pan_number = pan_match.group(0)

    dob_match = re.search(dob_regex, raw_text)
    if dob_match:
        details.date_of_birth = dob_match.group(0)

    # --- Step 2: Try NER first for Name extraction ---
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            details.name = ent.text.strip()
            break
    
    # --- Step 3: NEW - If NER fails, use our refined heuristic as a fallback ---
    if not details.name:
        lines = raw_text.split('\n')
        for line in lines:
            line = line.strip()
            # Check if the line looks like a name and is not a header
            if len(line) > 3 and line.isupper() and not any(char.isdigit() for char in line):
                words = set(line.split())
                if not words.intersection(EXCLUDE_KEYWORDS):
                    details.name = line
                    break # We found our name, so we can stop searching

    return details