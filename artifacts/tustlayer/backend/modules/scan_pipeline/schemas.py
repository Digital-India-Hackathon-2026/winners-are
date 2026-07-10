from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import time

from backend.modules.ocr.schemas import OCRResult
from backend.modules.fraud_intelligence.schemas import FraudMatchResult
from backend.modules.trust_score.schemas import TrustScoreResult
from backend.modules.app_forensics.schemas import AppForensicsResult


class ScanMetadata(BaseModel):
    execution_time_ms: int
    modules_executed: list[str]


class DeepfakeScanResult(BaseModel):
    deepfake_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    is_deepfake: bool = False
    manipulation_type: str = "unknown"
    signals: List[str] = Field(default_factory=list)
    error: Optional[str] = None


class VPAValidationResult(BaseModel):
    upi_id: Optional[str] = None
    vpa_handle_valid: bool = False
    vpa_exists: Optional[bool] = None
    registered_name: Optional[str] = None
    name_match: Optional[bool] = None
    error: Optional[str] = None


class DeterministicFlags(BaseModel):
    foreign_currency_detected: bool = False
    utr_format_violation: bool = False
    utr_dummy_pattern: bool = False
    exif_editing_software: bool = False
    exif_software_name: Optional[str] = None
    timestamp_late_night: bool = False
    replay_detected: bool = False
    replay_count: int = 0
    score_breakdown: Optional[Dict[str, int]] = None
    triggered_caps: Optional[List[str]] = None


class FinalScanResponse(BaseModel):
    """
    v2.0 Cinematic Monolithic Payload.
    Designed for frontend progressive disclosure.
    """
    success: bool = True
    metadata: ScanMetadata

    # Core Results
    trust_score_data: TrustScoreResult

    # Supporting Evidence
    ocr_data: OCRResult
    fraud_intelligence_data: FraudMatchResult
    app_forensics: Optional[AppForensicsResult] = None

    # v2.0 New Evidence Layers
    deepfake_data: Optional[DeepfakeScanResult] = None
    vpa_validation_data: Optional[VPAValidationResult] = None
    deterministic_flags: Optional[DeterministicFlags] = None

    # Session & Rate Limit Context
    anonymous_session_id: Optional[str] = None
    remaining_scans: int = Field(-1, description="Scans remaining for guest, or -1 if authenticated")
