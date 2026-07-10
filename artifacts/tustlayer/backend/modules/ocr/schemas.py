"""
TrustLayer AI – OCR Schemas
Pydantic models for OCR extraction results
"""
from typing import Optional, Dict
from pydantic import BaseModel, Field


class ExtractedFields(BaseModel):
    """Structured fields extracted from a UPI payment screenshot."""
    # Core fields (used by AI extraction)
    payment_amount: Optional[str] = Field(None, description="The extracted payment amount, e.g., '₹4,500'")
    receiver_name: Optional[str] = Field(None, description="Name of the person/business receiving the payment")
    upi_id: Optional[str] = Field(None, description="UPI VPA e.g. 9876543210@ybl")
    transaction_reference: Optional[str] = Field(None, description="UTR/Ref ID (12-16 digit number)")
    payment_app: Optional[str] = Field(None, description="App name (Google Pay / PhonePe / Paytm / BHIM / CRED)")
    timestamp: Optional[str] = Field(None, description="Date and time of the transaction")
    payment_status: str = Field(default="UNKNOWN", description="SUCCESS / FAILED / PENDING / UNKNOWN")
    ui_authenticity: str = Field(default="UNKNOWN", description="LIKELY_GENUINE / SUSPICIOUS / UNKNOWN")
    app_detection_confidence: float = Field(default=0.0, ge=0.0, le=1.0)

    # Backward-compat aliases (used by scan_pipeline, supabase_client, etc.)
    upi_transaction_id: Optional[str] = Field(None, description="12-digit UPI transaction reference number (alias for transaction_reference)")
    payment_app_name: Optional[str] = Field(None, description="App used (alias for payment_app)")

    def model_post_init(self, __context) -> None:
        """Auto-sync aliased fields for backward compatibility."""
        # transaction_reference ↔ upi_transaction_id
        if self.transaction_reference and not self.upi_transaction_id:
            self.upi_transaction_id = self.transaction_reference
        elif self.upi_transaction_id and not self.transaction_reference:
            self.transaction_reference = self.upi_transaction_id

        # payment_app ↔ payment_app_name
        if self.payment_app and not self.payment_app_name:
            self.payment_app_name = self.payment_app
        elif self.payment_app_name and not self.payment_app:
            self.payment_app = self.payment_app_name


class OCRResult(BaseModel):
    """Complete OCR extraction result."""
    fields: ExtractedFields = Field(default_factory=ExtractedFields)
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Overall confidence of the extraction")
    used_fallback: bool = Field(default=False, description="True if Tesseract recovery was used")
    raw_text: Optional[str] = Field(None, description="Raw text extracted (mainly for debugging)")
    image_quality_score: float = Field(default=0.5, ge=0.0, le=1.0, description="Estimated image quality")
    ocr_pass_count: int = Field(default=1, ge=0, description="Number of OCR passes run")


def calculate_weighted_confidence(
    fields: ExtractedFields,
    consensus_counts: Optional[Dict[str, int]] = None,
    total_passes: int = 1
) -> float:
    """
    Calculate weighted confidence score based on extracted fields.

    Weights reflect importance of each field for trust assessment:
    - payment_amount: 30% (most critical)
    - receiver_name: 20%
    - timestamp: 15%
    - payment_app: 15%
    - upi_id: 10%
    - transaction_reference: 10%

    consensus_counts and total_passes are kept for signature compat but ignored
    (no longer needed with single AI pass).
    """
    weights = {
        "payment_amount": 0.30,
        "receiver_name": 0.20,
        "timestamp": 0.15,
        "payment_app": 0.15,
        "upi_id": 0.10,
        "transaction_reference": 0.10,
    }

    confidence = sum(
        w for field_name, w in weights.items()
        if getattr(fields, field_name, None) not in (None, "", "UNKNOWN", "N/A")
    )

    return round(min(1.0, max(0.0, confidence)), 3)
