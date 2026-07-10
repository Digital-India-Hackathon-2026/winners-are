"""
TrustLayer AI – QR Inspector Engine v2.0
Extracts and forensically analyzes QR codes from payment screenshots.
Uses OpenCV QRCodeDetector (no libzbar system dep required).
"""
import re
from typing import Optional, List, Tuple
from urllib.parse import urlparse, parse_qs


VALID_UPI_HANDLES = {
    "@ybl", "@ibl", "@axl", "@paytm",
    "@okaxis", "@okicici", "@oksbi", "@okhdfcbank",
    "@upi", "@apl", "@abfspay", "@naviaxis",
    "@waicici", "@waxis", "@yapl", "@rapl",
    "@pnb", "@sbi", "@hdfc", "@icici", "@axis",
    "@federal", "@indus", "@kotak", "@fbl",
    "@barodampay", "@mahb", "@sib", "@idbi",
    "@centralbank", "@csbpay", "@dcb", "@jkb",
    "@kvb", "@lvb", "@scb", "@unionbank",
    "@zoicici", "@freecharge", "@airtelpaymentsbank",
}


def _parse_upi_uri(uri: str) -> Optional[dict]:
    """Parse a UPI URI like upi://pay?pa=xxx&pn=xxx&am=xxx"""
    try:
        if not uri.lower().startswith("upi://"):
            return None
        parsed = urlparse(uri)
        params = parse_qs(parsed.query)
        return {k: v[0] if v else None for k, v in params.items()}
    except Exception:
        return None


def _check_vpa_handle(vpa: Optional[str]) -> bool:
    if not vpa:
        return False
    lower = vpa.lower()
    return any(lower.endswith(h) for h in VALID_UPI_HANDLES)


class QRInspectorEngine:
    def extract_qr_codes(self, image_bytes: bytes) -> Tuple[List[str], int]:
        """
        Extract QR code data from image bytes using OpenCV.
        Returns (list_of_decoded_strings, count).
        """
        try:
            import cv2
            import numpy as np
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return [], 0

            detector = cv2.QRCodeDetector()
            # Try multi-QR first (OpenCV 4.5.4+)
            try:
                retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(img)
                if retval and decoded_info:
                    valid = [d for d in decoded_info if d]
                    return valid, len(valid)
            except AttributeError:
                pass

            # Fallback to single QR
            data, _, _ = detector.detectAndDecode(img)
            if data:
                return [data], 1
            return [], 0

        except ImportError:
            print("[QR-INSPECTOR] OpenCV not available — attempting PIL fallback")
            return self._pil_qr_fallback(image_bytes)
        except Exception as e:
            print(f"[QR-INSPECTOR] QR extraction error: {e}")
            return [], 0

    def _pil_qr_fallback(self, image_bytes: bytes) -> Tuple[List[str], int]:
        """PIL-based fallback using pyzbar if available."""
        try:
            from PIL import Image
            import io
            try:
                from pyzbar.pyzbar import decode as pyzbar_decode
                img = Image.open(io.BytesIO(image_bytes))
                decoded = pyzbar_decode(img)
                texts = [d.data.decode("utf-8", errors="replace") for d in decoded]
                return texts, len(texts)
            except ImportError:
                pass
        except Exception as e:
            print(f"[QR-INSPECTOR] PIL fallback failed: {e}")
        return [], 0

    def analyze_qr_data(self, qr_text: str) -> dict:
        """
        Analyze a single decoded QR string.
        Returns dict with is_upi, payload, risk_signals.
        """
        risk_signals = []
        payload = None
        is_upi = False
        foreign_currency = False
        amount_hardcoded = False
        unknown_vpa = False
        suspicious_uri = False

        if qr_text.lower().startswith("upi://"):
            is_upi = True
            params = _parse_upi_uri(qr_text)
            if params:
                pa = params.get("pa")
                pn = params.get("pn")
                am = params.get("am")
                cu = params.get("cu", "INR")
                tn = params.get("tn")
                tr = params.get("tr")
                mc = params.get("mc")
                sign = params.get("sign")
                mode = params.get("mode")

                payload = {
                    "raw_uri": qr_text,
                    "pa": pa, "pn": pn, "am": am, "tn": tn,
                    "tr": tr, "mc": mc, "cu": cu, "mode": mode, "sign": sign
                }

                # Risk checks
                if cu and cu.upper() != "INR":
                    foreign_currency = True
                    risk_signals.append(f"Foreign currency in QR: {cu}")

                if am:
                    try:
                        amt = float(am)
                        amount_hardcoded = True
                        if amt <= 0 or amt > 2_000_000:
                            risk_signals.append(f"Suspicious hardcoded amount: ₹{amt}")
                        else:
                            risk_signals.append(f"Amount hardcoded in QR: ₹{amt} (verify before scanning)")
                    except ValueError:
                        risk_signals.append(f"Invalid amount value in QR: {am}")

                vpa_valid = _check_vpa_handle(pa)
                if not vpa_valid:
                    unknown_vpa = True
                    if pa:
                        risk_signals.append(f"Unknown VPA handle in QR: {pa}")

                if not sign:
                    risk_signals.append("No digital signature in UPI QR (unverified merchant)")

        elif re.match(r'https?://', qr_text, re.I):
            suspicious_uri = True
            risk_signals.append(f"QR contains URL (not UPI): {qr_text[:80]}")
        else:
            risk_signals.append(f"Non-UPI QR content: {qr_text[:60]}")

        return {
            "is_upi": is_upi,
            "payload": payload,
            "foreign_currency": foreign_currency,
            "amount_hardcoded": amount_hardcoded,
            "unknown_vpa": unknown_vpa,
            "suspicious_uri": suspicious_uri,
            "risk_signals": risk_signals,
            "vpa_handle_valid": not unknown_vpa if is_upi else False,
        }
