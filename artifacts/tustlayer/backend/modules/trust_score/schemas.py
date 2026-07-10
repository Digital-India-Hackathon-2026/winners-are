from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class TrustScoreInput(BaseModel):
    # ── Phase 3: OCR Inputs ─────────────────────────────────────────────────
    upi_transaction_id_valid: bool = Field(..., description="True if UTR is 12 digits and matches checksum")
    payment_amount_valid: bool = Field(..., description="True if amount matches expected transaction format")

    # ── Phase 2: Fraud Intelligence ─────────────────────────────────────────
    fraud_fingerprint_match: bool = Field(..., description="True if matched a known scam template")
    fraud_match_confidence: float = Field(default=0.0, description="Confidence of the template match")

    # ── Layer Inputs (v1 compat) ─────────────────────────────────────────────
    metadata_anomalies_detected: int = Field(default=0, description="Number of EXIF/compression anomalies")
    layout_inconsistencies_detected: int = Field(default=0, description="Number of UI layout flaws")
    ai_visual_flags: int = Field(default=0, description="Visual anomalies flagged by LLM")

    # ── OCR Quality Signals ─────────────────────────────────────────────────
    ocr_confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    app_detection_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    image_quality_score: float = Field(default=0.5, ge=0.0, le=1.0)
    fields_extracted_count: int = Field(default=0, ge=0)
    fields_total_count: int = Field(default=7, ge=1)

    # ── v2.0: Deterministic Flag Signals ────────────────────────────────────
    # UTR layer
    utr_format_violation: bool = Field(default=False, description="UTR present but not 12 digits")
    utr_dummy_pattern: bool = Field(default=False, description="UTR is all-zeros or obviously fake pattern")

    # VPA / Razorpay layer
    vpa_handle_valid: bool = Field(default=False, description="UPI handle regex matches known bank suffixes")
    vpa_exists_razorpay: Optional[bool] = Field(default=None, description="Razorpay live VPA lookup result; None if unchecked")
    vpa_name_match: Optional[bool] = Field(default=None, description="VPA registered name matches OCR receiver name")

    # Currency / Amount layer
    foreign_currency_detected: bool = Field(default=False, description="$ € £ or dollar/eur/usd found in receipt")
    amount_plausible: bool = Field(default=True, description="Amount is within ₹1–₹10,00,000 and uses ₹ symbol")

    # EXIF / Metadata layer
    exif_missing: bool = Field(default=False, description="True if no EXIF data was found")
    exif_editing_software: bool = Field(default=False, description="EXIF Software tag contains known editing tool")
    exif_software_name: Optional[str] = Field(default=None, description="Name of detected editing software")

    # App branding / forensics layer
    app_branding_match: bool = Field(default=False, description="Color fingerprint matches claimed payment app")
    ela_score: float = Field(default=0.0, description="Error Level Analysis anomaly score 0-1")

    # Deepfake detection layer
    deepfake_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Hive deepfake confidence 0–1")
    deepfake_detected: bool = Field(default=False, description="deepfake_score > 0.30")

    # Timestamp layer
    timestamp_valid: bool = Field(default=True, description="Timestamp is within normal business hours and plausible date")
    timestamp_late_night: bool = Field(default=False, description="Timestamp between 00:00–05:59 IST (unusual)")

    # Replay / uniqueness layer
    replay_detected: bool = Field(default=False, description="Same UTR seen in DB within 24 hours")
    replay_count: int = Field(default=0, description="Number of times this UTR has been submitted")


class TrustScoreResult(BaseModel):
    trust_score: float = Field(..., ge=0.0, le=100.0, description="0 to 100. Higher = more trustworthy.")
    risk_level: RiskLevel
    fraud_probability: float = Field(..., ge=0.0, le=1.0)
    confidence_reasoning: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    verdict: Optional[str] = Field(None, description="Forensic verdict state, e.g. 'Likely Authentic'")
    extraction_quality_label: Optional[str] = Field(None, description="Human-readable OCR quality label")
    what_to_do_next: Optional[List[str]] = Field(default=None, description="Actionable next steps for the user")

    # v2.0 score breakdown (for frontend transparency)
    score_breakdown: Optional[dict] = Field(default=None, description="Point contribution per criterion")
