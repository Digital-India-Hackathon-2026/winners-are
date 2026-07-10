from pydantic import BaseModel, Field
from typing import Optional, List


class DocumentThreatResult(BaseModel):
    success: bool = False
    document_type: str = Field("unknown", description="image/pdf/unknown")
    page_count: int = 0

    # Steganography
    steganography_suspected: bool = False
    steganography_signals: List[str] = Field(default_factory=list)

    # URL / link extraction
    urls_found: List[str] = Field(default_factory=list)
    suspicious_urls: List[str] = Field(default_factory=list)
    url_risk_level: str = "UNKNOWN"
    url_analysis: List[dict] = Field(default_factory=list, description="Per-URL risk analysis with reasons")

    # Embedded file threats
    embedded_files_found: bool = False
    embedded_file_count: int = 0

    # PDF-specific
    pdf_javascript_found: bool = False
    pdf_auto_action_found: bool = False

    # Overall
    risk_level: str = Field("UNKNOWN", description="LOW / MEDIUM / HIGH / UNKNOWN")
    risk_signals: List[str] = Field(default_factory=list)
    explanation: str = ""
    error: Optional[str] = None
