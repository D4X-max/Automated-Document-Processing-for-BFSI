from pydantic import BaseModel
from typing import Optional
from typing import Optional, Union 

class PANCardDetails(BaseModel):   # for PAN
    pan_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    name: Optional[str] = None

class AadhaarCardDetails(BaseModel):   # for Aadhaar
    aadhaar_number: Optional[str] = None
    name: Optional[str] = None
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    
# Find the UnifiedProcessingResult class and add the new field
class UnifiedProcessingResult(BaseModel):
    document_type: str
    is_successfully_parsed: bool
    is_duplicate: Optional[bool] = None 
    data: Optional[Union[PANCardDetails, AadhaarCardDetails]] = None
    
class VoterIDCardDetails(BaseModel):
    voter_id: Optional[str] = None
    name: Optional[str] = None
    name_hindi: Optional[str] = None



