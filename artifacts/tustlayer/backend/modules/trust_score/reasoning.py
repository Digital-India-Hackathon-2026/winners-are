import re
import logging
from typing import List, Optional
from backend.modules.trust_score.schemas import TrustScoreInput, RiskLevel
from backend.core.ai_orchestrator import AIReasoningOrchestrator

logger = logging.getLogger(__name__)

# Known payment-domain nouns always considered valid anchors
PAYMENT_DOMAIN_TERMS = {
    "upi", "vpa", "utr", "qr", "imps", "neft", "rtgs", "bhim",
    "phonepe", "paytm", "googlepay", "gpay", "amazonpay", "whatsapp",
    "razorpay", "payment", "transaction", "receipt", "screenshot",
    "bank", "account", "ifsc", "rupee", "inr", "₹", "amount", "balance",
    "fraud", "fake", "manipulated", "edited", "deepfake", "exif",
    "metadata", "timestamp", "branding", "logo", "layout", "tamper",
    "receiver", "sender", "transfer", "credit", "debit", "success",
    "failed", "pending", "verified", "validated", "authentic",
}


def _extract_nouns(text: str) -> set:
    """Extract meaningful word tokens from a sentence (lowercase, alpha only, len>=4)."""
    return {w for w in re.findall(r"[a-zA-Z₹]{4,}", text.lower())}


def _is_grounded(bullet: str, data: TrustScoreInput) -> bool:
    """
    Returns True if at least one key noun in the bullet overlaps with:
      - OCR raw_text extracted from the image
      - Known payment domain terms
      - Known data fields (app name, receiver name, etc.)
    Returns False (hallucination detected) only if there is ZERO overlap.
    """
    bullet_nouns = _extract_nouns(bullet)
    if not bullet_nouns:
        return True  # empty — don't discard

    # Build the grounding corpus from all available context
    grounding_corpus: set = set(PAYMENT_DOMAIN_TERMS)

    raw = getattr(data, "raw_text", None)
    if raw:
        grounding_corpus |= _extract_nouns(raw)

    for field in ("receiver_name", "payment_amount", "upi_id",
                  "upi_transaction_id", "payment_app_name", "exif_software_name"):
        val = getattr(data, field, None)
        if val:
            grounding_corpus |= _extract_nouns(str(val))

    return bool(bullet_nouns & grounding_corpus)


def _ground_filter(bullets: List[str], data: TrustScoreInput, source: str) -> List[str]:
    """Filter bullets; log a warning for each discarded hallucination."""
    grounded, discarded = [], []
    for b in bullets:
        if _is_grounded(b, data):
            grounded.append(b)
        else:
            discarded.append(b)
    if discarded:
        logger.warning(
            "[GROUNDING-GUARD] %s: discarded %d ungrounded bullet(s): %s",
            source, len(discarded), discarded
        )
    return grounded


class ConfidenceReasoningGenerator:
    def __init__(self, ai_orchestrator: AIReasoningOrchestrator):
        self.ai = ai_orchestrator

    async def generate_reasons(self, data: TrustScoreInput) -> List[str]:
        # Deterministic reasoning guarantees a response even if AI times out
        reasons = []

        if getattr(data, 'deepfake_score', 0) > 0.4:
            reasons.append(f"High probability ({data.deepfake_score:.0%}) of AI manipulation or deepfake.")
        elif getattr(data, 'deepfake_detected', False):
            reasons.append("AI generation or manipulation markers detected in the image.")

        if getattr(data, 'exif_editing_software', False):
            reasons.append(f"Image was saved or modified using editing software ({getattr(data, 'exif_software_name', 'Unknown')}).")
        if getattr(data, 'metadata_anomalies_detected', 0) > 0:
            reasons.append(f"Detected {data.metadata_anomalies_detected} missing or altered metadata tags (potential screenshot editing).")

        if getattr(data, 'ela_score', 0) > 0.6:
            reasons.append("Error Level Analysis (ELA) detected signs of digital tampering or splicing.")

        if getattr(data, 'fraud_fingerprint_match', False):
            reasons.append("Image layout strongly matches known fake payment generator templates.")
        if not getattr(data, 'app_branding_match', True):
            reasons.append("The logo or layout does not match the official payment app design.")

        if getattr(data, 'foreign_currency_detected', False):
            reasons.append("Foreign currency symbol detected, which is unusual for standard domestic UPI.")
        if getattr(data, 'utr_format_violation', False):
            reasons.append("UTR format is invalid (not 12 digits).")
        elif getattr(data, 'utr_dummy_pattern', False):
            reasons.append("UTR contains repeated/dummy patterns (e.g., 123456).")

        if getattr(data, 'timestamp_late_night', False):
            reasons.append("Transaction occurred at an unusual late-night hour.")

        if getattr(data, 'vpa_exists_razorpay', None) is False:
            reasons.append("The receiver's UPI ID (VPA) does not exist or is inactive.")

        if not reasons:
            if getattr(data, 'deepfake_score', 0) < 0.1 and getattr(data, 'metadata_anomalies_detected', 0) == 0:
                reasons.append("No signs of AI manipulation or metadata tampering.")
            if getattr(data, 'app_branding_match', False) and not getattr(data, 'fraud_fingerprint_match', False):
                reasons.append("App layout and branding appear consistent with the official app.")
            if getattr(data, 'vpa_exists_razorpay', None):
                reasons.append("Receiver UPI ID was successfully validated.")
            if not reasons:
                reasons.append("Standard verification checks passed successfully.")

        context_data = data.model_dump()
        context_data['task'] = 'generate_reasons'
        try:
            ai_reasons = await self.ai.get_reasoning_with_fallback(context_data)
            # Grounding guard: discard bullets not traceable to OCR/known fields
            ai_reasons = _ground_filter(ai_reasons, data, "ConfidenceReasoningGenerator")
            # Add up to 1 unique grounded AI reason to supplement
            for r in ai_reasons:
                if not any(r.lower()[:20] in exist.lower() for exist in reasons):
                    reasons.append(r)
                    break
            return reasons[:6]
        except Exception:
            return reasons[:6]


class RecommendationEngine:
    def __init__(self, ai_orchestrator: AIReasoningOrchestrator):
        self.ai = ai_orchestrator

    async def generate_recommendations(self, risk: RiskLevel, data: TrustScoreInput) -> List[str]:
        context_data = data.model_dump()
        context_data['task'] = 'generate_recommendations'

        # Hardcoded actionable advice per user request
        base_actions = []
        if risk == RiskLevel.HIGH:
            base_actions = [
                "🚨 DO NOT release goods or services. This receipt appears manipulated.",
                "🚔 Report to Cybercrime: File a complaint on cybercrime.gov.in with the sender's details.",
                "📞 Contact your bank immediately if you have already transferred money.",
                "🛑 Demand legit payment: Ask the sender to pay via a verified method or escrow."
            ]
        elif risk == RiskLevel.MEDIUM:
            base_actions = [
                "⚠️ Proceed with caution. Some anomalies were detected.",
                "🔍 Check your bank app directly to confirm the amount was credited before proceeding."
            ]
        else:
            base_actions = [
                "✅ Payment proof appears authentic.",
                "💡 Always verify your bank balance directly before handing over high-value goods."
            ]

        try:
            ai_recs = await self.ai.get_recommendations_with_fallback(risk.value, context_data)
            # Grounding guard: discard hallucinated recommendations
            ai_recs = _ground_filter(ai_recs, data, "RecommendationEngine")
            # Combine: deterministic at top, limit AI to 1 point
            return base_actions + [r for r in ai_recs if r not in base_actions][:1]
        except Exception:
            return base_actions
