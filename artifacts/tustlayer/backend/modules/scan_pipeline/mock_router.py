from fastapi import APIRouter, HTTPException, status
from backend.modules.scan_pipeline.schemas import FinalScanResponse, ScanMetadata
from backend.modules.trust_score.schemas import TrustScoreResult, RiskLevel
from backend.modules.ocr.schemas import OCRResult, ExtractedFields
from backend.modules.fraud_intelligence.schemas import FraudMatchResult
from backend.modules.app_forensics.schemas import AppForensicsResult

router = APIRouter(prefix="/api/v1/mock", tags=["Mock Scenarios"])

@router.get("/scenario/{scenario_name}", response_model=FinalScanResponse)
async def get_mock_scenario(scenario_name: str):
    """
    Returns pre-calculated JSON payloads without hitting heavy ML models.
    Perfect for bulletproof live demos.
    Scenarios: perfect_receipt, fraud_template_match, photoshop_detected
    """
    
    if scenario_name == "perfect_receipt":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1200, modules_executed=["OCR", "AppForensics", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=100.0,
                risk_level=RiskLevel.LOW,
                fraud_probability=0.0,
                confidence_reasoning=["All deterministic and visual checks passed successfully"],
                recommended_actions=["Payment proof appears authentic"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="123456789012", payment_amount="1000.00"),
                confidence_score=0.95, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(fingerprint_match=False, match_confidence=0.0, match_count=0),
            app_forensics=AppForensicsResult(
                detected_app="Google Pay",
                app_authenticity_score=1.0,
                logo_match=True,
                layout_consistency="HIGH",
                font_consistency="NORMAL",
                suspected_clone=False,
                forensic_explanation="Authentic Google Pay layout structure and confirmation spacing matched."
            )
        )
        
    elif scenario_name == "fraud_template_match":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1450, modules_executed=["OCR", "AppForensics", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=26.0,
                risk_level=RiskLevel.HIGH,
                fraud_probability=0.99,
                confidence_reasoning=["Known scam template pattern detected", "App text-color mismatch flags cloned Paytm screenshot"],
                recommended_actions=["Do not release goods or services", "Request live transfer verification or alternative proof"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="555555555555", payment_amount="50000.00"),
                confidence_score=0.88, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(
                fingerprint_match=True, match_confidence=0.98, match_count=1, fraud_type="Cloned Paytm Receipt"
            ),
            app_forensics=AppForensicsResult(
                detected_app="Suspicious clone UI",
                app_authenticity_score=0.25,
                logo_match=False,
                layout_consistency="LOW",
                font_consistency="SUSPICIOUS",
                suspected_clone=True,
                forensic_explanation="This screenshot claims to be Paytm, but verification shows standard cyan banners are absent, indicating a cloned interface."
            )
        )
        
    elif scenario_name == "photoshop_detected":
        return FinalScanResponse(
            metadata=ScanMetadata(execution_time_ms=1300, modules_executed=["OCR", "AppForensics", "FraudIntelligence", "Metadata", "TrustScore"]),
            trust_score_data=TrustScoreResult(
                trust_score=72.0,
                risk_level=RiskLevel.MEDIUM,
                fraud_probability=0.22,
                confidence_reasoning=["Image metadata indicates post-capture editing", "Irregular crop spacing detected in PhonePe layout banner"],
                recommended_actions=["Verify payment receipt directly in your banking app"]
            ),
            ocr_data=OCRResult(
                fields=ExtractedFields(upi_transaction_id="987654321098", payment_amount="250.00"),
                confidence_score=0.90, used_fallback=False
            ),
            fraud_intelligence_data=FraudMatchResult(fingerprint_match=False, match_confidence=0.0, match_count=0),
            app_forensics=AppForensicsResult(
                detected_app="PhonePe",
                app_authenticity_score=0.72,
                logo_match=True,
                layout_consistency="MEDIUM",
                font_consistency="NORMAL",
                suspected_clone=False,
                forensic_explanation="PhonePe layout matched, but pixel-level EXIF compression checks indicate timestamp font overlays were modified."
            )
        )
        
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mock scenario not found.")

