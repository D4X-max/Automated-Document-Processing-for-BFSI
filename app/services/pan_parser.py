import re
import spacy
from app.models import PANCardDetails

# Load the spaCy model
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    NLP = spacy.load("en_core_web_sm")

## REFINE 1: Define a clear list of header keywords to exclude from name candidates.
EXCLUDE_KEYWORDS = {
    'INCOME', 'TAX', 'DEPARTMENT', 'GOVT', 'INDIA', 'GOVERNMENT', 
    'PERMANENT', 'ACCOUNT', 'NUMBER', 'NAME', 'FATHER'
}

def _clean_text(text: str) -> str:
    """Removes unwanted characters and extra whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def _extract_pan_number(text: str) -> str | None:
    """Finds the PAN number using a more forgiving regex."""
    ## REFINE 2: Use a less strict regex that finds 10-character alphanumeric strings,
    # as PAN numbers are often the only string of this format on the card.
    pan_regex = r'\b[A-Z0-9]{10}\b'
    matches = re.findall(pan_regex, text)
    for match in matches:
        # Validate the structure: 5 letters, 4 numbers, 1 letter.
        if re.match(r'[A-Z]{5}[0-9]{4}[A-Z]', match):
            return match
    return None

def _extract_dob(text: str) -> str | None:
    """Finds the Date of Birth using a standard regex."""
    dob_regex = r'\d{2}/\d{2}/\d{4}'
    match = re.search(dob_regex, text)
    if match:
        return match.group(0)
    return None

def _extract_name(doc: spacy.tokens.doc.Doc, raw_text: str) -> str | None:
    """
    Extracts the most likely name by collecting all possible candidates from NER and
    heuristics, filtering them, and choosing the best one.
    """
    candidate_names = []
    
    # --- Stage 1: Collect candidates from NER ---
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            candidate_names.append(ent.text)

    # --- Stage 2: Collect candidates from heuristics ---
    lines = raw_text.split('\n')
    for line in lines:
        cleaned_line = _clean_text(line)
        # Heuristic: A name is often all uppercase, has 2-5 words, and no digits.
        if cleaned_line.isupper() and 2 <= len(cleaned_line.split()) <= 5 and not any(char.isdigit() for char in cleaned_line):
            candidate_names.append(cleaned_line)
            
    # --- Stage 3: Filter and select the best candidate ---
    clean_candidates = []
    for name in candidate_names:
        name_upper = name.upper()
        # A valid candidate must not contain any of the excluded keywords.
        if not any(keyword in name_upper for keyword in EXCLUDE_KEYWORDS):
            clean_candidates.append(_clean_text(name))
            
    if not clean_candidates:
        return None

    ## REFINE 3: Choose the longest candidate. This is a very effective heuristic.
    return max(clean_candidates, key=len)


# --- Main Parsing Function ---
def parse_pan_details(raw_text: str) -> PANCardDetails:
    """
    The main orchestrator function to parse PAN card details using a robust strategy.
    """
    text_upper = raw_text.upper()
    doc = NLP(raw_text)

    pan_number = _extract_pan_number(text_upper)
    dob = _extract_dob(text_upper)
    name = _extract_name(doc, raw_text)

    return PANCardDetails(
        pan_number=pan_number,
        date_of_birth=dob,
        name=name
    )


