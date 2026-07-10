from pydantic import BaseModel, Field
from typing import Optional


class VPALookupResult(BaseModel):
    upi_id: str
    vpa_handle_valid: bool = Field(False, description="Handle matches known bank suffix regex")
    vpa_exists: Optional[bool] = Field(None, description="True/False from Razorpay live lookup; None if unchecked")
    registered_name: Optional[str] = Field(None, description="Name registered with the VPA in Razorpay")
    name_match: Optional[bool] = Field(None, description="registered_name matches OCR receiver_name")
    error: Optional[str] = None
