"""
TrustLayer AI – OCR Engine v2.1
AI-first OCR using NVIDIA Nemotron-VL as primary.
Tesseract is used ONLY for targeted field recovery when AI fails.
"""
import re
import io
from PIL import Image
from typing import Optional, Dict
from backend.modules.ocr.schemas import ExtractedFields, OCRResult, calculate_weighted_confidence


def _compute_image_quality(image_bytes: bytes) -> float:
    """Estimate image quality 0.0-1.0. Used for Trust Score micro-adjustment."""
    try:
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        pixel_count = w * h
        file_size = len(image_bytes)

        resolution_score = min(1.0, max(0.1, pixel_count / (1080 * 1920)))

        bpp = file_size / max(1, pixel_count)
        if bpp > 0.3:
            compression_score = 1.0
        elif bpp > 0.1:
            compression_score = 0.9
        elif bpp > 0.05:
            compression_score = 0.7
        else:
            compression_score = 0.4

        return round(min(1.0, max(0.05, (resolution_score * 0.4) + (compression_score * 0.6))), 3)
    except Exception:
        return 0.5


def _map_nvidia_response_to_fields(data: Dict) -> ExtractedFields:
    """Map NVIDIA Nemotron JSON output → ExtractedFields schema."""
    def clean(v) -> Optional[str]:
        if v is None or v == "null" or str(v).strip() in ("", "N/A", "Unknown"):
            return None
        return str(v).strip()

    payment_app = clean(data.get("payment_app"))
    upi_id = clean(data.get("upi_id"))

    # Secondary app detection from UPI handle if model missed it
    if not payment_app and upi_id:
        handle = upi_id.lower()
        if any(h in handle for h in ["@ybl", "@ibl", "@axl"]):
            payment_app = "PhonePe"
        elif "@paytm" in handle:
            payment_app = "Paytm"
        elif any(h in handle for h in ["@okaxis", "@okicici", "@oksbi", "@okhdfcbank"]):
            payment_app = "Google Pay"
        elif "@upi" in handle:
            payment_app = "BHIM"

    # App detection confidence
    app_conf_map = {
        "Google Pay": 0.92, "PhonePe": 0.91, "Paytm": 0.90,
        "BHIM": 0.85, "CRED": 0.85, "Amazon Pay": 0.88
    }
    app_conf = app_conf_map.get(payment_app, 0.0) if payment_app else 0.0

    return ExtractedFields(
        payment_amount=clean(data.get("payment_amount")),
        receiver_name=clean(data.get("receiver_name")),
        upi_id=upi_id,
        transaction_reference=clean(data.get("transaction_reference")),
        payment_app=payment_app,
        timestamp=clean(data.get("timestamp")),
        payment_status=clean(data.get("payment_status")) or "UNKNOWN",
        ui_authenticity=clean(data.get("ui_authenticity")) or "UNKNOWN",
        app_detection_confidence=app_conf,
    )


class NvidiaFirstOCREngine:
    """AI-first OCR engine. NVIDIA Nemotron is primary. Tesseract is recovery only."""

    async def extract(self, image_bytes: bytes) -> OCRResult:
        from backend.integrations.nvidia_client import NvidiaOCRExtractor

        quality_score = _compute_image_quality(image_bytes)
        print(f"[OCR-ENGINE] Image quality: {quality_score:.2f}")

        # ── STEP 1: NVIDIA Nemotron-VL (PRIMARY) ─────────────────────────
        raw_text_extracted = None
        try:
            extractor = NvidiaOCRExtractor()
            raw_fields = await extractor.extract_fields(image_bytes)
            fields = _map_nvidia_response_to_fields(raw_fields)
            confidence = calculate_weighted_confidence(fields)
            raw_text_extracted = raw_fields.get("raw_text_content")
            print(f"[OCR-ENGINE] NVIDIA confidence: {confidence:.2f}")

            # ── STEP 2: Tesseract targeted recovery (only if NVIDIA mostly failed) ──
            extracted_count = sum(1 for v in [
                fields.payment_amount, fields.receiver_name,
                fields.upi_id, fields.transaction_reference
            ] if v)

            if extracted_count < 2:
                print("[OCR-ENGINE] NVIDIA got <2 fields, trying Tesseract recovery")
                fields, raw_text_extracted = self._tesseract_recovery(image_bytes, fields)
                confidence = calculate_weighted_confidence(fields)

            return OCRResult(
                fields=fields,
                confidence_score=confidence,
                used_fallback=False,
                raw_text=raw_text_extracted,
                image_quality_score=quality_score,
                ocr_pass_count=1,
            )

        except Exception as e:
            print(f"[OCR-ENGINE] NVIDIA FAILED: {e}. Using Tesseract fallback.")
            fields, raw_text_extracted = self._tesseract_recovery(image_bytes, ExtractedFields())
            confidence = calculate_weighted_confidence(fields)
            return OCRResult(
                fields=fields,
                confidence_score=max(confidence, 0.1),
                used_fallback=True,
                raw_text=raw_text_extracted,
                image_quality_score=quality_score,
                ocr_pass_count=1,
            )

    def _tesseract_recovery(self, image_bytes: bytes, fields: ExtractedFields) -> tuple:
        """Try Tesseract for specific missing fields only. Returns (fields, raw_text)."""
        try:
            import pytesseract
            img = Image.open(io.BytesIO(image_bytes))
            # Upscale for better Tesseract accuracy
            img = img.resize((img.width * 2, img.height * 2), Image.Resampling.LANCZOS)
            text = pytesseract.image_to_string(img)
            print(f"[TESSERACT-RECOVERY] Extracted {len(text)} chars")
            return self._parse_tesseract_fields(text, fields), text
        except Exception as e:
            print(f"[TESSERACT-RECOVERY] Failed: {e}")
            return fields, None

    def _parse_tesseract_fields(self, text: str, fields: ExtractedFields) -> ExtractedFields:
        """Extract only missing fields from Tesseract text."""
        if not fields.payment_amount:
            m = re.search(r'(?:₹|Rs\.?)\s*[\d,]+(?:\.\d{1,2})?', text)
            if m:
                fields.payment_amount = m.group(0)

        if not fields.upi_id:
            m = re.search(r'[\w.\-]+@[\w]+', text)
            if m:
                fields.upi_id = m.group(0)

        if not fields.transaction_reference:
            m = re.search(r'\b\d{12,16}\b', text)
            if m:
                fields.transaction_reference = m.group(0)

        if fields.payment_status == "UNKNOWN":
            if re.search(r'success', text, re.I):
                fields.payment_status = "SUCCESS"
            elif re.search(r'failed', text, re.I):
                fields.payment_status = "FAILED"

        return fields


# Backward compat alias for existing imports
TesseractEngine = NvidiaFirstOCREngine
