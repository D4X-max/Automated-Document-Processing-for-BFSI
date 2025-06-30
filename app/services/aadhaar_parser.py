import re
import spacy
from app.models import AadhaarCardDetails

# Load the spaCy model
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    NLP = spacy.load("en_core_web_sm")

## REFINE 1: A comprehensive list of keywords and labels to exclude from names.
EXCLUDE_KEYWORDS = {
    'GOVERNMENT', 'INDIA', 'UNIQUE', 'IDENTIFICATION', 'AUTHORITY', 
    'AADHAAR', 'ENROLLMENT', 'BHARAT', 'SARKAR', 'भारत', 'सरकार', 
    'जन्म', 'तिथि', 'DOB', 'BIRTH', 'NAME', 'FATHER'
}

def _clean_text(text: str) -> str:
    """Removes unwanted characters and extra whitespace."""
    return re.sub(r'[\n\r\s]+', ' ', text).strip()

def _extract_aadhaar_number(text: str) -> str | None:
    """
    Finds a 12-digit number by concatenating all digits from the text block.
    This is robust against numbers split by newlines or spaces.
    """
    ## REFINE 2: This is the robust concatenation strategy.
    all_digits = re.sub(r'\D', '', text)
    if len(all_digits) >= 12:
        # Often the Aadhaar is the first long number. We can add more logic here if needed.
        # For now, let's search for any 12-digit sequence within the concatenated digits.
        match = re.search(r'\d{12}', all_digits)
        if match:
            return match.group(0)
    return None

def _extract_dob(text: str) -> str | None:
    """Finds a Date of Birth using a standard dd/mm/yyyy regex."""
    dob_regex = r'\b(\d{2}/\d{2}/\d{4})\b'
    match = re.search(dob_regex, text)
    if match:
        return match.group(0)
    return None

def _extract_gender(text: str) -> str | None:
    """Finds gender using regex with word boundaries and Hindi words."""
    if re.search(r'\b(Female|FEMALE|महिला)\b', text):
        return "Female"
    if re.search(r'\b(Male|MALE|पुरुष)\b', text):
        return "Male"
    return None

def _extract_name(doc: spacy.tokens.doc.Doc, lines: list[str]) -> str | None:
    """
    Extracts the name using a robust multi-stage filtering strategy.
    """
    candidate_names = []
    
    # Stage 1: Get candidates from NER
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            candidate_names.append(ent.text)
            
    # Stage 2: Get candidate from "line before DOB" heuristic
    for i, line in enumerate(lines):
        if re.search(r'\d{2}/\d{2}/\d{4}', line):
            if i > 0:
                candidate_names.append(lines[i-1])

    if not candidate_names:
        return None

    # Stage 3: Rigorously filter candidates
    clean_candidates = []
    for name in candidate_names:
        cleaned_name = _clean_text(name)
        name_upper = cleaned_name.upper()
        
        ## REFINE 3: A much stronger set of validation rules.
        # 1. Must not contain any excluded keyword.
        # 2. Must not contain any digits.
        # 3. Must be of a reasonable length (e.g., more than one word).
        if (not any(keyword in name_upper for keyword in EXCLUDE_KEYWORDS) and
            not any(char.isdigit() for char in cleaned_name) and
            len(cleaned_name.split()) > 1):
            clean_candidates.append(cleaned_name)

    if not clean_candidates:
        return None

    # Stage 4: Return the longest valid candidate.
    return max(clean_candidates, key=len)


# --- Main Parsing Function ---
def parse_aadhaar_details(raw_text: str) -> AadhaarCardDetails:
    """
    The main orchestrator function to parse Aadhaar card details.
    """
    doc = NLP(raw_text)
    lines = raw_text.split('\n')

    aadhaar_number = _extract_aadhaar_number(raw_text) # Pass the whole text
    dob = _extract_dob(raw_text)
    gender = _extract_gender(raw_text)
    name = _extract_name(doc, lines)

    return AadhaarCardDetails(
        aadhaar_number=aadhaar_number,
        date_of_birth=dob,
        gender=gender,
        name=name
    )


