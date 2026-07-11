from pydantic import BaseModel, Field
from typing import Optional, List

class URLScanDetail(BaseModel):
    url: str
    status: str = Field(..., description="Safe / Needs Verification / Likely Fraud")
    reason: str

class MessageInspectionResult(BaseModel):
    success: bool = True
    message_text: str
    language: str = "en"
    urls_found: List[str] = Field(default_factory=list)
    url_analysis: List[URLScanDetail] = Field(default_factory=list)
    phone_numbers_found: List[str] = Field(default_factory=list)
    upi_ids_found: List[str] = Field(default_factory=list)
    emails_found: List[str] = Field(default_factory=list)
    keywords_detected: List[str] = Field(default_factory=list)
    is_forwarded: bool = False
    forwarded_many_times: bool = False
    
    score: float = 100.0
    verdict: str = Field(..., description="Likely Fraud / Needs Verification / Verified")
    summary: str
    concerns: List[str] = Field(default_factory=list)
    action_steps: List[str] = Field(default_factory=list)
    
    whatsapp_response: str = ""
    error: Optional[str] = None
