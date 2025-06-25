import re
import spacy
from app.models import AadhaarCardDetails

# We can reuse the same NLP model loaded in the other parser,
# but for modularity, let's load it here too.
# A more advanced setup might share one loaded model instance.
try:
    NLP = spacy.load("en_core_web_sm")
except OSError:
    from spacy.cli import download
    download("en_core_web_sm")
    NLP = spacy.load("en_core_web_sm")

def parse_aadhaar_details(raw_text: str) -> AadhaarCardDetails:
    """
    Parses raw OCR text to find Aadhaar number, name, DOB, and gender.
    """
    details = AadhaarCardDetails()
    doc = NLP(raw_text)

    # 1. Regex for Aadhaar Number
    # Format: 12 digits, possibly with spaces. e.g., '1234 5678 9012'
    aadhaar_regex = r"\d{4}\s?\d{4}\s?\d{4}"
    aadhaar_match = re.search(aadhaar_regex, raw_text)
    if aadhaar_match:
        details.aadhaar_number = aadhaar_match.group(0).replace(" ", "")

    # 2. Regex for Date of Birth
    # Often has a "DOB:" prefix. Format: dd/mm/yyyy
    dob_regex = r"(?:DOB|Date of Birth)\s*[:]?\s*(\d{2}/\d{2}/\d{4})"
    dob_match = re.search(dob_regex, raw_text, re.IGNORECASE)
    if dob_match:
        details.date_of_birth = dob_match.group(1)

    # 3. --- IMPROVED GENDER EXTRACTION ---
    # We will now look for the keywords on the same line.
    lines = raw_text.split('\n')
    gender_found = False
    for line in lines:
        if "Female" in line or "FEMALE" in line:
            details.gender = "Female"
            gender_found = True
            break # Found Female, stop searching
    
    # Only check for Male if Female was not found on any line.
    # This prevents a random "Male" in the address from overwriting the correct gender.
    if not gender_found:
        for line in lines:
            if "Male" in line or "MALE" in line:
                details.gender = "Male"
                break # Found Male, stop searching

    # 4. Use NER for Name extraction
    # We can look for a PERSON entity that is not also part of another line
    # like "Father's Name" - but for now, the first PERSON found is a good start.
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            details.name = ent.text.strip()
            break
    
    return details
