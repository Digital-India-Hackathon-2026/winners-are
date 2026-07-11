from pydantic import BaseModel, Field
from typing import Optional, List


class UPIQRPayload(BaseModel):
    raw_uri: str = Field(..., description="Raw UPI URI decoded from QR code")
    pa: Optional[str] = Field(None, description="Payee address (UPI VPA)")
    pn: Optional[str] = Field(None, description="Payee name")
    am: Optional[str] = Field(None, description="Amount")
    tn: Optional[str] = Field(None, description="Transaction note")
    tr: Optional[str] = Field(None, description="Transaction reference")
    mc: Optional[str] = Field(None, description="Merchant category code")
    cu: Optional[str] = Field(None, description="Currency code (should be INR)")
    mode: Optional[str] = Field(None, description="Payment mode")
    sign: Optional[str] = Field(None, description="Digital signature")


class QRInspectionResult(BaseModel):
    success: bool = False
    qr_found: bool = False
    qr_count: int = 0
    is_upi_qr: bool = False
    upi_payload: Optional[UPIQRPayload] = None

    # Risk signals
    foreign_currency: bool = False
    amount_hardcoded: bool = False
    unknown_vpa_handle: bool = False
    vpa_handle_valid: bool = False
    multiple_qr_codes: bool = False
    suspicious_uri: bool = False

    risk_level: str = Field("UNKNOWN", description="LOW / MEDIUM / HIGH / UNKNOWN")
    risk_signals: List[str] = Field(default_factory=list)
    resolved_url: Optional[str] = Field(None, description="Final URL after redirect resolution")
    explanation: str = ""
    error: Optional[str] = None
