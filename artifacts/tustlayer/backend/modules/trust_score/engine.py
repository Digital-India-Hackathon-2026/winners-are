"""
TrustLayer AI – Trust Score Engine v2.0
PRD-specified additive point formula with hard caps.

Max possible = 25+20+15+15+10+8+7+5 = 105 → clamped to 100.
Hard caps are applied AFTER additive accumulation.
"""
from typing import Dict, Tuple
from backend.modules.trust_score.schemas import TrustScoreInput


# ── Point values (PRD Section 4.1) ──────────────────────────────────────────
POINTS = {
    "utr_valid":         25,
    "vpa_exists":        20,
    "app_branding":      15,
    "exif_clean":        15,
    "deepfake_clean":    10,
    "timestamp_valid":    8,
    "amount_plausible":   7,
    "no_replay":          5,
}

# ── Hard caps (PRD Section 4.2) — applied to final score ────────────────────
CAP_FOREIGN_CURRENCY   = 10   # $ € £ in receipt
CAP_UTR_FORMAT_WRONG   = 15   # UTR present but not 12 digits
CAP_FRAUD_TEMPLATE     = 5    # Known scam pHash match > 0.80
CAP_EXIF_EDITING       = 40   # Editing software in EXIF
CAP_MISSING_EXIF       = 70   # Missing EXIF (high risk)
CAP_DEEPFAKE           = 25   # Deepfake score > 0.70
CAP_ELA_ANOMALY        = 40   # Error Level Analysis score > 0.8
CAP_VPA_NOT_EXIST      = 20   # Razorpay says VPA does not exist


class TrustScoreEngine:
    """
    v2.0 additive scoring engine per PRD.

    Score bands (target outputs):
        Fully verified (all green):    85–100   → LOW risk
        Mostly authentic:              65–84    → LOW risk
        Partial / uncertain:           40–64    → MEDIUM risk
        Multiple red flags:            20–39    → HIGH risk
        Clear fraud signals:            0–19    → HIGH risk
    """

    @staticmethod
    def calculate_base_score(data: TrustScoreInput) -> Tuple[float, Dict[str, int]]:
        """
        Returns (raw_additive_score, breakdown_dict).
        Caller applies hard caps and clamps to 0–100.
        """
        breakdown: Dict[str, int] = {}

        # 1. UTR (+25) — skip if UTR format violation
        if data.upi_transaction_id_valid and not data.utr_format_violation and not data.utr_dummy_pattern:
            breakdown["utr_valid"] = POINTS["utr_valid"]
        else:
            breakdown["utr_valid"] = 0

        # 2. VPA exists in Razorpay (+20)
        # vpa_exists_razorpay=None means unchecked (give partial credit based on handle format)
        if data.vpa_exists_razorpay is True:
            breakdown["vpa_exists"] = POINTS["vpa_exists"]
        elif data.vpa_exists_razorpay is None and data.vpa_handle_valid:
            # Partial credit when no live check but handle format is valid
            breakdown["vpa_exists"] = POINTS["vpa_exists"] // 2  # +10
        else:
            breakdown["vpa_exists"] = 0

        # 3. App branding match (+15)
        breakdown["app_branding"] = POINTS["app_branding"] if data.app_branding_match else 0

        # 4. EXIF clean (+15)
        # If ELA score is somewhat high but below hard cap, penalize EXIF points
        if data.ela_score > 0.5:
            breakdown["exif_clean"] = 0
        elif not data.exif_editing_software and data.metadata_anomalies_detected == 0:
            breakdown["exif_clean"] = POINTS["exif_clean"]
        elif data.metadata_anomalies_detected <= 1 and not data.exif_editing_software:
            breakdown["exif_clean"] = POINTS["exif_clean"] // 2  # minor noise, partial
        else:
            breakdown["exif_clean"] = 0

        # 5. Deepfake clean (+10)
        if not data.deepfake_detected and data.deepfake_score < 0.30:
            breakdown["deepfake_clean"] = POINTS["deepfake_clean"]
        elif data.deepfake_score < 0.50:
            breakdown["deepfake_clean"] = POINTS["deepfake_clean"] // 2
        else:
            breakdown["deepfake_clean"] = 0

        # 6. Timestamp valid (+8)
        if data.timestamp_valid and not data.timestamp_late_night:
            breakdown["timestamp_valid"] = POINTS["timestamp_valid"]
        elif data.timestamp_valid:
            breakdown["timestamp_valid"] = POINTS["timestamp_valid"] // 2  # valid but late night
        else:
            breakdown["timestamp_valid"] = 0

        # 7. Amount plausible (+7)
        breakdown["amount_plausible"] = POINTS["amount_plausible"] if data.amount_plausible else 0

        # 8. No replay (+5)
        breakdown["no_replay"] = POINTS["no_replay"] if not data.replay_detected else 0

        raw_score = sum(breakdown.values())
        return float(raw_score), breakdown

    @staticmethod
    def apply_hard_caps(score: float, data: TrustScoreInput) -> Tuple[float, list]:
        """
        Apply PRD hard caps. Returns (capped_score, list_of_triggered_caps).
        """
        triggered = []

        if data.fraud_fingerprint_match and data.fraud_match_confidence > 0.80:
            if score > CAP_FRAUD_TEMPLATE:
                score = CAP_FRAUD_TEMPLATE
                triggered.append(f"Known fraud template match ({data.fraud_match_confidence:.0%} confidence) → cap {CAP_FRAUD_TEMPLATE}")

        if data.foreign_currency_detected:
            if score > CAP_FOREIGN_CURRENCY:
                score = CAP_FOREIGN_CURRENCY
                triggered.append(f"Foreign currency symbol detected → cap {CAP_FOREIGN_CURRENCY}")

        if data.utr_format_violation:
            if score > CAP_UTR_FORMAT_WRONG:
                score = CAP_UTR_FORMAT_WRONG
                triggered.append(f"UTR format invalid (not 12 digits) → cap {CAP_UTR_FORMAT_WRONG}")

        if data.exif_editing_software:
            if score > CAP_EXIF_EDITING:
                score = CAP_EXIF_EDITING
                triggered.append(f"Editing software in EXIF ({data.exif_software_name or 'unknown'}) → cap {CAP_EXIF_EDITING}")

        if data.exif_missing:
            if score > CAP_MISSING_EXIF:
                score = CAP_MISSING_EXIF
                triggered.append(f"No EXIF metadata found (suspicious for screenshot) → cap {CAP_MISSING_EXIF}")

        if data.ela_score > 0.8:
            if score > CAP_ELA_ANOMALY:
                score = CAP_ELA_ANOMALY
                triggered.append(f"High pixel-level error (ELA score {data.ela_score:.2f}) → cap {CAP_ELA_ANOMALY}")

        if data.deepfake_score > 0.70:
            if score > CAP_DEEPFAKE:
                score = CAP_DEEPFAKE
                triggered.append(f"Deepfake probability {data.deepfake_score:.0%} → cap {CAP_DEEPFAKE}")

        if data.vpa_exists_razorpay is False:
            if score > CAP_VPA_NOT_EXIST:
                score = CAP_VPA_NOT_EXIST
                triggered.append(f"VPA does not exist per Razorpay lookup → cap {CAP_VPA_NOT_EXIST}")

        return score, triggered

    @classmethod
    def calculate(cls, data: TrustScoreInput) -> Tuple[float, Dict[str, int], list]:
        """
        Full calculation. Returns (final_score_0_100, breakdown, triggered_caps).
        """
        raw_score, breakdown = cls.calculate_base_score(data)
        capped_score, caps_triggered = cls.apply_hard_caps(raw_score, data)
        final = max(0.0, min(100.0, round(capped_score, 2)))
        return final, breakdown, caps_triggered

    @classmethod
    def calculate_base_score_compat(cls, data: TrustScoreInput) -> float:
        """
        Backward-compat shim used by the old service layer.
        Returns just the final score (after caps).
        """
        final, _, _ = cls.calculate(data)
        return final
