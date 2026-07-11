"""
TrustLayer AI – Multi-Layer QR Verification Engine v2.2
Implements 13-point security verification per user specification.
Determines threat signals and applies deterministic scoring rules.
"""
import re
import hashlib
from typing import Optional, List, Tuple, Dict, Any
from urllib.parse import urlparse, parse_qs, parse_qsl

# PRD Section 12: 37 valid UPI bank suffixes
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
    # Paytm and Partner handles
    "@pthdfc", "@ptaxis", "@ptsbi", "@ptyes", "@superyes",
    # WhatsApp UPI handles
    "@waaxis", "@wahdfc", "@wasbi",
}

KNOWN_SCAM_PATTERNS = {
    "paytm-refund", "cashback-claim", "rewards-upi", "verify-gpay",
    "paytm.refund", "refund.collection", "cashback.offer"
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

def _classify_qr_type(qr_text: str) -> str:
    lower = qr_text.lower()
    if lower.startswith("upi://"):
        return "UPI Payment"
    elif re.match(r'^https?://', qr_text, re.I):
        return "Website URL"
    elif lower.startswith("mecard:") or lower.startswith("begin:vcard"):
        return "Contact"
    elif lower.startswith("mailto:"):
        return "Email"
    elif lower.startswith("smsto:") or lower.startswith("sms:"):
        return "SMS"
    elif lower.startswith("wifi:"):
        return "WiFi"
    elif qr_text.strip():
        if all(c.isprintable() or c.isspace() for c in qr_text):
            return "Plain Text"
    return "Unknown"

def _parse_and_validate_upi_uri(uri: str) -> dict:
    validation = {
        "format_valid": True,
        "missing_mandatory": [],
        "duplicate_params": [],
        "invalid_encoding": False,
        "params": {}
    }
    try:
        if not uri.lower().startswith("upi://"):
            validation["format_valid"] = False
            return validation
        parsed = urlparse(uri)
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        seen_keys = set()
        for k, v in query_pairs:
            if k in seen_keys:
                if k not in validation["duplicate_params"]:
                    validation["duplicate_params"].append(k)
            seen_keys.add(k)
            validation["params"][k] = v
            if "%" in v:
                try:
                    from urllib.parse import unquote
                    unquote(v, errors="strict")
                except Exception:
                    validation["invalid_encoding"] = True
        if "pa" not in validation["params"] or not validation["params"]["pa"]:
            validation["missing_mandatory"].append("pa (Payee Address)")
    except Exception:
        validation["format_valid"] = False
    return validation

def _evaluate_domain_reputation(url: str) -> Tuple[float, List[str]]:
    score = 100.0
    signals = []
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if parsed.scheme.lower() != "https":
            score -= 20
            signals.append("Non-secure protocol (HTTP instead of HTTPS)")
        shorteners = {
            "bit.ly", "tinyurl.com", "t.co", "goo.gl", "rebrand.ly",
            "is.gd", "buff.ly", "adf.ly", "ow.ly", "bit.do", "lnkd.in"
        }
        if any(domain == s or domain.endswith("." + s) for s in shorteners):
            score -= 30
            signals.append(f"Uses a URL shortener service: {domain}")
        suspicious_tlds = {
            "xyz", "top", "click", "club", "info", "online", "cc", "ws",
            "biz", "download", "work", "fit", "gdn", "icu", "vip", "loan"
        }
        tld = domain.split(".")[-1]
        if tld in suspicious_tlds:
            score -= 25
            signals.append(f"Suspicious top-level domain (.{tld})")
        ip_pattern = re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$')
        if ip_pattern.match(domain.split(":")[0]):
            score -= 40
            signals.append(f"IP-address based URL domain: {domain}")
        if "xn--" in domain:
            score -= 30
            signals.append("Internationalized Domain Name (potential homograph phishing attack)")
    except Exception:
        pass
    return max(0.0, score), signals

def _cross_validate_ocr(qr_type: str, upi_params: dict, ocr_result: Any) -> Tuple[Optional[bool], List[str]]:
    if not ocr_result or not hasattr(ocr_result, "fields") or not ocr_result.fields:
        return None, []
    mismatches = []
    fields = ocr_result.fields
    ocr_amount_str = fields.payment_amount
    qr_amount_str = upi_params.get("am")
    if ocr_amount_str and qr_amount_str:
        ocr_num = re.sub(r'[^\d.]', '', ocr_amount_str)
        qr_num = re.sub(r'[^\d.]', '', qr_amount_str)
        try:
            if float(ocr_num) != float(qr_num):
                mismatches.append(f"Amount mismatch: Surrounding text shows ₹{ocr_num}, but QR requests ₹{qr_num}")
        except ValueError:
            pass
    ocr_receiver = fields.receiver_name
    qr_payee = upi_params.get("pn")
    if ocr_receiver and qr_payee:
        clean_ocr = re.sub(r'[^a-z0-9\s]', '', ocr_receiver.lower()).strip()
        clean_qr = re.sub(r'[^a-z0-9\s]', '', qr_payee.lower()).strip()
        words_ocr = set(clean_ocr.split())
        words_qr = set(clean_qr.split())
        if words_ocr and words_qr and not (words_ocr & words_qr):
            mismatches.append(f"Merchant mismatch: Surrounding text shows '{ocr_receiver}', but QR belongs to '{qr_payee}'")
    ocr_upi = fields.upi_id
    qr_upi = upi_params.get("pa")
    if ocr_upi and qr_upi:
        if ocr_upi.strip().lower() != qr_upi.strip().lower():
            mismatches.append(f"UPI ID mismatch: Surrounding text shows {ocr_upi}, but QR has {qr_upi}")
    raw_ocr_lower = (ocr_result.raw_text or "").lower()
    utility_keywords = ["bill", "electricity", "water", "gas", "tax", "police", "challan", "government"]
    if qr_upi:
        is_personal_vpa = not upi_params.get("mc")
        if any(kw in raw_ocr_lower for kw in utility_keywords) and is_personal_vpa:
            vpa_owner_clean = qr_payee.lower() if qr_payee else ""
            if re.match(r'^\d{10}@', qr_upi) or not any(x in vpa_owner_clean for x in ["utility", "board", "limited", "power", "bill", "tax"]):
                mismatches.append("Context mismatch: Surrounding text claims utility/government bill, but QR links to a personal VPA account")
    cross_matched = len(mismatches) == 0 if (ocr_amount_str or ocr_receiver or ocr_upi) else None
    return cross_matched, mismatches

def _check_intent_spoofing(qr_text: str, ocr_text: str = "") -> List[str]:
    warnings = []
    text_to_check = (qr_text + " " + ocr_text).lower()
    receive_keywords = ["receive", "refund", "cashback", "claim", "credit", "earn", "reward"]
    if qr_text.lower().startswith("upi://"):
        if any(kw in text_to_check for kw in receive_keywords):
            warnings.append(
                "Payment Intent Spoofing: Surrounding context or QR note mentions 'receiving' or 'claiming' money, "
                "but scanning this UPI QR code will actually DEDUCT money from your account."
            )
    return warnings

def _analyze_image_authenticity(image_bytes: bytes) -> List[str]:
    issues = []
    try:
        import cv2
        import numpy as np
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return ["Failed to decode image pixels"]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        if laplacian_var < 80:
            issues.append(f"Image is highly blurry (variance: {laplacian_var:.1f})")
        h, w = gray.shape
        resolution = w * h
        file_size = len(image_bytes)
        bpp = file_size / max(1, resolution)
        if bpp < 0.04:
            issues.append(f"High compression artifacts detected (low quality: {bpp:.3f} BPP)")
        try:
            _, encoded_img = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 90])
            decoded_img = cv2.imdecode(encoded_img, cv2.IMREAD_COLOR)
            diff = cv2.absdiff(img, decoded_img)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(diff_gray, 20, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if len(contours) > 50:
                issues.append("Suspicious localized compression mismatch (possible pasted QR region)")
        except Exception:
            pass
    except Exception as e:
        print(f"[QR-FORENSICS] Image analysis warning: {e}")
    return issues

def _calculate_phash(image_bytes: bytes) -> str:
    try:
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(image_bytes)).convert("L").resize((8, 8), Image.Resampling.LANCZOS)
        pixels = list(img.getdata())
        avg = sum(pixels) / 64
        bits = "".join(["1" if p >= avg else "0" for p in pixels])
        return f"{int(bits, 2):016x}"
    except Exception:
        return ""

def _check_scam_database(qr_text: str) -> Tuple[bool, str]:
    sha256_hash = hashlib.sha256(qr_text.encode("utf-8")).hexdigest()
    lower_text = qr_text.lower()
    for pattern in KNOWN_SCAM_PATTERNS:
        if pattern in lower_text:
            return True, sha256_hash
    return False, sha256_hash


class QRInspectorEngine:
    def extract_qr_codes(self, image_bytes: bytes) -> Tuple[List[str], int]:
        try:
            import cv2
            import numpy as np
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if img is None:
                return [], 0
            detector = cv2.QRCodeDetector()
            try:
                retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(img)
                if retval and decoded_info:
                    valid = [d for d in decoded_info if d]
                    return valid, len(valid)
            except AttributeError:
                pass
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

    async def analyze_qr_data(
        self,
        qr_text: str,
        image_bytes: Optional[bytes] = None,
        ocr_result: Optional[Any] = None
    ) -> Dict[str, Any]:
        risk_signals = []
        payload = None
        is_upi = False
        foreign_currency = False
        amount_hardcoded = False
        unknown_vpa = False
        suspicious_uri = False
        final_url = None
        google_safe_browsing_threat = False

        # Classify Type
        qr_type = _classify_qr_type(qr_text)
        
        # Duplicate checks / database hash
        is_known_scam, sha256_hash = _check_scam_database(qr_text)
        p_hash = _calculate_phash(image_bytes) if image_bytes else ""
        
        # Image Authenticity Forensics
        authenticity_issues = _analyze_image_authenticity(image_bytes) if image_bytes else []

        # Surrounding OCR raw text
        raw_ocr_text = ocr_result.raw_text if ocr_result and hasattr(ocr_result, "raw_text") else ""

        # Score & Rule Engine
        score = 100.0

        if qr_type == "UPI Payment":
            is_upi = True
            upi_val = _parse_and_validate_upi_uri(qr_text)
            params = upi_val["params"]
            
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

            # 1. Format & validation
            if not upi_val["format_valid"]:
                score -= 50
                risk_signals.append("Invalid UPI URI format structure")
            if upi_val["missing_mandatory"]:
                score -= 30
                risk_signals.append(f"Missing mandatory parameters: {', '.join(upi_val['missing_mandatory'])}")
            if upi_val["duplicate_params"]:
                score -= 20
                risk_signals.append(f"Duplicate UPI parameters found: {', '.join(upi_val['duplicate_params'])}")
            if upi_val["invalid_encoding"]:
                score -= 15
                risk_signals.append("Invalid percent encoding detected in parameters")

            # 2. Field risk checks
            if cu and cu.upper() != "INR":
                foreign_currency = True
                score -= 20
                risk_signals.append(f"Foreign currency in QR: {cu}")
            if am:
                try:
                    amt = float(am)
                    amount_hardcoded = True
                    if amt <= 0 or amt > 2_000_000:
                        score -= 20
                        risk_signals.append(f"Suspicious hardcoded amount: ₹{amt}")
                    else:
                        risk_signals.append(f"Amount hardcoded in QR: ₹{amt}")
                except ValueError:
                    score -= 10
                    risk_signals.append(f"Invalid amount value in QR: {am}")

            vpa_valid = _check_vpa_handle(pa)
            if not vpa_valid:
                unknown_vpa = True
                score -= 30
                if pa:
                    risk_signals.append(f"Unknown VPA handle suffix in QR: {pa}")
            if not sign:
                score -= 10
                risk_signals.append("No digital signature in UPI QR (unverified personal QR)")

            # 3. Intent spoofing check
            intent_warnings = _check_intent_spoofing(qr_text, raw_ocr_text)
            for warn in intent_warnings:
                score -= 60
                risk_signals.append(warn)

            # 4. OCR cross validation
            cross_matched, mismatches = _cross_validate_ocr(qr_type, params, ocr_result)
            for mis in mismatches:
                if "Amount mismatch" in mis:
                    score -= 40
                elif "Merchant mismatch" in mis:
                    score -= 30
                else:
                    score -= 30
                risk_signals.append(mis)

        elif qr_type == "Website URL":
            final_url = qr_text
            domain_score, domain_signals = _evaluate_domain_reputation(qr_text)
            score -= (100 - domain_score)
            risk_signals.extend(domain_signals)

            try:
                import httpx
                async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                    response = await client.head(qr_text)
                    final_url = str(response.url)
                    if final_url != qr_text:
                        risk_signals.append(f"QR redirects to: {final_url}")
                        redir_score, redir_signals = _evaluate_domain_reputation(final_url)
                        score -= (100 - redir_score)
                        risk_signals.extend(redir_signals)
            except Exception as redirect_err:
                print(f"[QR-INSPECTOR] Failed to resolve redirects: {redirect_err}")
                score -= 15
                risk_signals.append("⚠ Failed to verify URL security destination.")

            # Google Safe Browsing
            from backend.integrations.safe_browsing_client import check_urls
            try:
                urls_to_check = list(set([qr_text, final_url]))
                sb_result = await check_urls(urls_to_check)
                for checked_url, res_data in sb_result.items():
                    if res_data.get("is_threat"):
                        google_safe_browsing_threat = True
                        score -= 80
                        threat_type = res_data.get("threat_type", "SUSPICIOUS")
                        risk_signals.append(f"Flagged by Google Safe Browsing as {threat_type}")
                        break
            except Exception as e:
                print(f"[QR-INSPECTOR] Google Safe Browsing check failed: {e}")

        else:
            if qr_type == "Unknown":
                score -= 30
                risk_signals.append(f"Unidentifiable or corrupted QR payload content")
            else:
                risk_signals.append(f"Non-payment QR content ({qr_type}): {qr_text[:60]}")

        # Image Forensic scoring
        if authenticity_issues:
            score -= 50
            risk_signals.extend(authenticity_issues)

        # Duplicate Scam DB
        if is_known_scam:
            score = 0
            risk_signals.append("CRITICAL: Decoded payload matches previously reported fraud patterns in database")

        score = max(0.0, min(100.0, score))

        if score >= 80:
            verdict = "Verified"
        elif score >= 40:
            verdict = "Needs Verification"
        else:
            verdict = "Likely Fraud"

        guidance = ""
        if is_upi and payload:
            payee = payload.get("pn") or "Unspecified Payee"
            amount_display = f"₹{payload.get('am')}" if payload.get("am") else "User-entered amount"
            guidance += f"Payee: {payee} | UPI ID: {payload.get('pa')} | Amount: {amount_display}\n"
            if any("mismatch" in sig for sig in risk_signals):
                guidance += "⚠ WARNING: SURROUNDING RECEIPT DETAILS DO NOT MATCH THIS QR PAYLOAD.\n"
            if any("Spoofing" in sig for sig in risk_signals):
                guidance += "🚨 FRAUD ALERT: THIS QR CODE WILL CHARGE MONEY FROM YOUR ACCOUNT, IT WILL NOT CREDIT YOU MONEY.\n"
            else:
                guidance += "👉 Scanning this QR code will initiate a PAY transaction from your wallet to the recipient."
        elif final_url:
            guidance += f"Links to: {final_url}\n"
            if google_safe_browsing_threat:
                guidance += "🚨 DANGER: GOOGLE SAFE BROWSING HAS FLAGGED THIS SITE AS A MALICIOUS THREAT.\n"
            else:
                guidance += "👉 Verify the URL address before logging in or entering credentials."
        else:
            guidance += f"Decoded content type: {qr_type}. Contents: {qr_text[:120]}"

        return {
            "is_upi": is_upi,
            "payload": payload,
            "foreign_currency": foreign_currency,
            "amount_hardcoded": amount_hardcoded,
            "unknown_vpa": unknown_vpa,
            "suspicious_uri": suspicious_uri,
            "risk_signals": risk_signals,
            "vpa_handle_valid": not unknown_vpa if is_upi else False,
            "google_safe_browsing_threat": google_safe_browsing_threat,
            "resolved_url": final_url,
            "qr_type": qr_type,
            "qr_format_valid": upi_val["format_valid"] if is_upi else True,
            "missing_mandatory_params": upi_val["missing_mandatory"] if is_upi else [],
            "duplicate_params": upi_val["duplicate_params"] if is_upi else [],
            "ocr_cross_matched": locals().get("cross_matched", None),
            "ocr_mismatches": locals().get("mismatches", []),
            "safe_browsing_threat": google_safe_browsing_threat,
            "domain_reputation_score": locals().get("domain_score", 100.0),
            "image_authenticity_issues": authenticity_issues,
            "verdict": verdict,
            "guidance": guidance.strip(),
            "hash_sha256": sha256_hash,
            "score": score
        }
