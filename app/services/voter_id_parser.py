import re
from app.models import VoterIDCardDetails
# We don't need spaCy here as a label-based approach is more reliable for Voter IDs.

## REFINE 1: Create helper functions for clean, maintainable logic.

def _clean_text(text: str) -> str:
    """Removes unwanted characters, colons, and extra whitespace."""
    text = text.replace(':', '').strip()
    return re.sub(r'\s+', ' ', text)

def _is_hindi(text: str) -> bool:
    """
    Checks if a string contains characters in the Devanagari (Hindi) Unicode range.
    This is a highly reliable way to distinguish the languages.
    """
    return bool(re.search(r'[\u0900-\u097F]', text))

def _extract_voter_id(text: str) -> str | None:
    """Finds the Voter ID (Epic No.) using a forgiving two-step process."""
    # Step 1: Find all 10-character alphanumeric strings.
    potential_ids = re.findall(r'\b[A-Z0-9]{10}\b', text.upper())
    
    # Step 2: Validate against the specific LLLNNNNNNN pattern.
    for pid in potential_ids:
        if re.match(r'[A-Z]{3}\d{7}', pid):
            return pid
    return None

def _extract_names(raw_text: str) -> tuple[str | None, str | None]:
    """
    Extracts English and Hindi names by finding labels and then classifying the text.
    """
    lines = raw_text.split('\n')
    candidate_names = []

    ## REFINE 2: Improve label-based extraction to be more flexible.
    for i, line in enumerate(lines):
        # Check if the label is on the line.
        if "Name" in line or "नाम" in line:
            # Case 1: Name is on the same line (e.g., "Name: JOHN DOE")
            parts = line.split(':')
            if len(parts) > 1 and parts[1].strip():
                candidate_names.append(parts[1].strip())
            
            # Case 2: Name is on the next line
            elif i + 1 < len(lines) and lines[i+1].strip():
                candidate_names.append(lines[i+1].strip())

    english_name, hindi_name = None, None
    
    ## REFINE 3: Separate candidates into English/Hindi using our helper.
    for name in candidate_names:
        if _is_hindi(name):
            # If we find a new, longer Hindi name, replace the old one.
            if not hindi_name or len(name) > len(hindi_name):
                hindi_name = _clean_text(name)
        else:
            # If we find a new, longer English name, replace the old one.
            if not english_name or len(name) > len(english_name):
                english_name = _clean_text(name)
                
    return english_name, hindi_name

# --- Main Parsing Function ---
def parse_voter_id_details(raw_text: str) -> VoterIDCardDetails:
    """
    The main orchestrator function to parse Voter ID card details.
    """
    voter_id = _extract_voter_id(raw_text)
    name_eng, name_hin = _extract_names(raw_text)

    return VoterIDCardDetails(
        voter_id=voter_id,
        name=name_eng,
        name_hindi=name_hin
    )

