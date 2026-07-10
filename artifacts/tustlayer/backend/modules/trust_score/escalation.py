"""
TrustLayer AI – Risk Escalation Layer v2.0
Applies graduated verdicts on top of the v2 additive score.
"""
from typing import Tuple
from backend.modules.trust_score.schemas import TrustScoreInput, RiskLevel


class RiskEscalationLayer:
    """
    Graduated verdict system — maps numeric score → verdict + risk level.

    Key principles:
    - OCR failure ≠ fraud.  Poor extraction → "Verification Recommended", not "Likely Fake".
    - "Likely Fake" is ONLY used when explicit fraud signals are present (cap at ≤25).
    - Hard-capped scores (foreign currency, deepfake, editing software) drive HIGH risk directly.
    """

    @staticmethod
    def _compute_extraction_quality_label(data: TrustScoreInput) -> str:
        ocr = data.ocr_confidence
        field_ratio = data.fields_extracted_count / max(1, data.fields_total_count)
        iq = data.image_quality_score

        if ocr >= 0.85 and field_ratio >= 0.7:
            return "High Quality Extraction"
        elif ocr >= 0.6 and field_ratio >= 0.5:
            return "Good Extraction"
        elif ocr >= 0.4 and field_ratio >= 0.3:
            return "Partial Extraction"
        elif ocr >= 0.2:
            return "Low Quality Image — Limited Extraction" if iq < 0.3 else "Low OCR Confidence"
        else:
            return "Very Low Quality Image — Extraction Unreliable" if iq < 0.2 else "Minimal Extraction — Verification Recommended"

    @staticmethod
    def evaluate(data: TrustScoreInput, base_score: float) -> Tuple[float, RiskLevel, float, str]:
        """
        Returns (final_score, risk_level, fraud_probability, verdict).
        base_score is the output of TrustScoreEngine.calculate() — already capped.
        """
        score = base_score

        # ── ABSOLUTE OVERRIDES (explicit fraud evidence) ──────────────────────

        # Known scam pHash match with high confidence
        if data.fraud_fingerprint_match and data.fraud_match_confidence > 0.80:
            return (0.0, RiskLevel.HIGH, 0.99, "Confirmed Fraud Pattern")

        # Deepfake probability > 90% is definitive
        if data.deepfake_score > 0.90:
            return (max(0.0, min(score, 5.0)), RiskLevel.HIGH, 0.97, "Likely AI-Generated")

        # Foreign currency + UTR violation together = definitive fake
        if data.foreign_currency_detected and data.utr_format_violation:
            return (max(0.0, min(score, 5.0)), RiskLevel.HIGH, 0.96, "Likely Fake")

        # Editing software found in EXIF — hard evidence of tampering
        if data.exif_editing_software:
            final = max(0.0, min(score, 40.0))
            if final <= 20:
                return (final, RiskLevel.HIGH, 0.88, "Likely Edited")
            return (final, RiskLevel.MEDIUM, 0.65, "Possible Tampering")

        # Foreign currency alone
        if data.foreign_currency_detected:
            return (max(0.0, min(score, 10.0)), RiskLevel.HIGH, 0.92, "Likely Fake")

        # UTR completely absent + amount absent — may be OCR failure, not fraud
        if not data.upi_transaction_id_valid and not data.payment_amount_valid:
            if data.ocr_confidence < 0.3:
                final = min(score, 50.0)
                return (final, RiskLevel.MEDIUM, 0.25, "Verification Recommended")
            else:
                final = min(score, 38.0)
                return (final, RiskLevel.MEDIUM, 0.45, "Needs Review")

        # ── GRADUATED VERDICTS (score-based) ─────────────────────────────────

        if score >= 85.0:
            verdict = "Verified"
            risk = RiskLevel.LOW
            prob = max(0.02, (100.0 - score) / 250.0)

        elif score >= 70.0:
            verdict = "Likely Authentic"
            risk = RiskLevel.LOW
            prob = max(0.05, (100.0 - score) / 200.0)

        elif score >= 55.0:
            verdict = "Partial Verification"
            risk = RiskLevel.MEDIUM
            prob = (100.0 - score) / 150.0

        elif score >= 35.0:
            verdict = "Low Confidence"
            risk = RiskLevel.MEDIUM
            prob = (100.0 - score) / 100.0

        elif score >= 20.0:
            verdict = "Needs Review"
            risk = RiskLevel.HIGH
            prob = min(0.80, (100.0 - score) / 100.0)

        else:
            verdict = "Likely Fake"
            risk = RiskLevel.HIGH
            prob = min(0.97, (100.0 - score) / 100.0)

        return (score, risk, round(prob, 3), verdict)
