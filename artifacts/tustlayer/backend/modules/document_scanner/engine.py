"""
TrustLayer AI – Document Scanner Engine v2.1
Analyzes images and PDFs for:
  - Steganography (LSB noise analysis via numpy)
  - Embedded URLs / phishing links (with brand impersonation + TLD analysis)
  - PDF JavaScript / auto-actions
  - Embedded files
"""
import io
import re
from typing import List, Tuple, Dict, Optional
from urllib.parse import urlparse


# ── Suspicious TLDs commonly used in phishing ─────────────────────────────────
SUSPICIOUS_TLDS = {
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".buzz", ".club",
    ".work", ".icu", ".fun", ".monster", ".rest", ".cam", ".surf", ".click",
    ".link", ".live", ".wang", ".site", ".online", ".space", ".store",
    ".quest", ".cfd", ".sbs", ".uno", ".best", ".lol", ".hair",
}

# ── URL shorteners (always suspicious in financial docs) ──────────────────────
URL_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "is.gd", "v.gd",
    "ow.ly", "buff.ly", "adf.ly", "cutt.ly", "rb.gy", "shorturl.at",
    "tiny.cc", "lnkd.in", "surl.li", "rebrand.ly",
}

# ── Indian bank & payment brands (for impersonation detection) ────────────────
INDIAN_BRAND_KEYWORDS = {
    "sbi", "hdfc", "icici", "axis", "kotak", "pnb", "bob", "canara",
    "union", "idbi", "rbl", "federal", "indusind", "bandhan", "yes",
    "paytm", "phonepe", "googlepay", "gpay", "bhim", "cred", "fampay",
    "razorpay", "bharatpe", "mobikwik", "freecharge", "airtel",
    "jio", "npci", "upi", "neft", "imps", "rtgs",
    "aadhaar", "aadhar", "pan", "kyc",
}

# ── Official domains whitelist (never flag these) ─────────────────────────────
OFFICIAL_DOMAINS = {
    # Banks
    "sbi.co.in", "onlinesbi.sbi", "retail.onlinesbi.sbi",
    "hdfcbank.com", "netbanking.hdfcbank.com",
    "icicibank.com", "infinity.icicibank.com",
    "axisbank.com", "omni.axisbank.com",
    "kotak.com", "netbanking.kotak.com",
    "pnbindia.in", "onlinebanking.pnbindia.in",
    "bankofbaroda.in", "bfrbl.bankofbaroda.in",
    "canarabank.com", "unionbankofindia.co.in",
    "idbibank.in", "rblbank.com", "federalbank.co.in",
    "indusind.com", "bandhanbank.com", "yesbank.in",
    # Payment apps
    "paytm.com", "phonepe.com", "pay.google.com",
    "bhimupi.org.in", "cred.club", "razorpay.com",
    "fampay.in", "mobikwik.com", "freecharge.in",
    "bharatpe.com", "airtel.in", "jio.com",
    # Government / regulatory
    "npci.org.in", "uidai.gov.in", "incometaxindia.gov.in",
    "rbi.org.in", "cybercrime.gov.in",
    # Common legitimate
    "google.com", "microsoft.com", "apple.com",
}

# ── Phishing keyword patterns in URL path/subdomain ──────────────────────────
PHISHING_PATH_PATTERNS = [
    r'upi[_-]?verify', r'kyc[_-]?update', r'kyc[_-]?verify',
    r'bank[_-]?login', r'account[_-]?verify', r'account[_-]?update',
    r'paytm[_-]?secure', r'phonepe[_-]?support', r'gpay[_-]?help',
    r'reward[_-]?claim', r'cashback[_-]?offer', r'lucky[_-]?winner',
    r'free[_-]?recharge', r'loan[_-]?approve', r'otp[_-]?verify',
    r'card[_-]?block', r'card[_-]?unblock', r'suspend',
    r'refund[_-]?process', r'claim[_-]?amount',
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # Raw IP addresses
]

URL_REGEX = re.compile(
    r'https?://[^\s<>"\')\]]+|www\.[^\s<>"\')\]]+',
    re.IGNORECASE
)


def _extract_urls_from_text(text: str) -> List[str]:
    return URL_REGEX.findall(text or "")


def _get_domain(url: str) -> str:
    """Extract the registrable domain from a URL."""
    try:
        parsed = urlparse(url if "://" in url else f"https://{url}")
        host = (parsed.hostname or "").lower().strip(".")
        return host
    except Exception:
        return ""


def _get_tld(domain: str) -> str:
    """Extract TLD (last dot-segment) from a domain."""
    parts = domain.rsplit(".", 1)
    if len(parts) == 2:
        return f".{parts[1]}"
    return ""


def _is_official_domain(domain: str) -> bool:
    """Check if domain or its parent is in the official whitelist."""
    if domain in OFFICIAL_DOMAINS:
        return True
    # Check parent: e.g. "netbanking.hdfcbank.com" → "hdfcbank.com"
    parts = domain.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[i:])
        if parent in OFFICIAL_DOMAINS:
            return True
    return False


def _analyze_url(url: str) -> Dict:
    """
    Deep analysis of a single URL. Returns risk classification with reasons.
    """
    lower = url.lower()
    domain = _get_domain(url)
    tld = _get_tld(domain)
    reasons = []
    risk = "SAFE"

    # 1. Skip official domains immediately
    if _is_official_domain(domain):
        return {"url": url, "risk": "SAFE", "reasons": ["Official/known domain"]}

    # 2. URL shorteners — always suspicious in financial context
    if domain in URL_SHORTENERS or any(domain.endswith(f".{s}") for s in URL_SHORTENERS):
        reasons.append(f"URL shortener ({domain}) — hides real destination")
        risk = "HIGH"

    # 3. Suspicious TLD
    if tld in SUSPICIOUS_TLDS:
        reasons.append(f"Suspicious TLD '{tld}' commonly used in phishing")
        risk = "HIGH"

    # 4. Brand impersonation — domain contains a bank/payment brand but isn't official
    for brand in INDIAN_BRAND_KEYWORDS:
        if brand in domain and not _is_official_domain(domain):
            reasons.append(f"Domain contains brand '{brand}' but is not an official domain")
            risk = "HIGH"
            break

    # 5. Phishing path/subdomain keywords
    for pattern in PHISHING_PATH_PATTERNS:
        if re.search(pattern, lower):
            reasons.append(f"Phishing keyword pattern detected in URL")
            risk = "HIGH"
            break

    # 6. Raw IP address
    if re.match(r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', lower):
        reasons.append("URL uses raw IP address instead of domain name")
        risk = "HIGH"

    # 7. Excessive subdomains (more than 3 dots in domain)
    if domain.count(".") >= 3:
        reasons.append(f"Excessive subdomains in domain ({domain})")
        if risk != "HIGH":
            risk = "MEDIUM"

    # 8. Homoglyph / typosquatting patterns
    typo_patterns = [
        (r'sbl\.', 'sbi'), (r'hdtc', 'hdfc'), (r'1cici', 'icici'),
        (r'ax1s', 'axis'), (r'paytrn', 'paytm'), (r'ph0nepe', 'phonepe'),
        (r'g00gle', 'google'), (r'amaz0n', 'amazon'),
    ]
    for pattern, brand in typo_patterns:
        if re.search(pattern, domain):
            reasons.append(f"Possible typosquatting of '{brand}'")
            risk = "HIGH"
            break

    # 9. If no signals found, mark as SAFE
    if not reasons:
        reasons.append("No suspicious indicators detected")

    return {"url": url, "risk": risk, "reasons": reasons}


def _is_suspicious_url(url: str) -> bool:
    """Quick check — returns True if URL has any risk signal."""
    result = _analyze_url(url)
    return result["risk"] in ("HIGH", "MEDIUM")


class DocumentScannerEngine:

    def analyze_image(self, image_bytes: bytes) -> dict:
        """Analyze a raster image for steganography and embedded URLs."""
        signals = []
        urls = []
        stego_suspected = False

        # ── Steganography: LSB noise analysis ────────────────────────────────
        try:
            import numpy as np
            from PIL import Image

            img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            arr = np.array(img, dtype=np.uint8)

            # Extract LSB plane of each channel
            lsb_r = arr[:, :, 0] & 1
            lsb_g = arr[:, :, 1] & 1
            lsb_b = arr[:, :, 2] & 1

            # Natural images have ~50% LSB entropy; stego raises it artificially
            total_pixels = lsb_r.size
            r_ratio = float(lsb_r.sum()) / total_pixels
            g_ratio = float(lsb_g.sum()) / total_pixels
            b_ratio = float(lsb_b.sum()) / total_pixels

            # Threshold: deviation from 0.5 < 0.03 in ALL channels = suspicious uniformity
            r_dev = abs(r_ratio - 0.5)
            g_dev = abs(g_ratio - 0.5)
            b_dev = abs(b_ratio - 0.5)

            if r_dev < 0.03 and g_dev < 0.03 and b_dev < 0.03:
                stego_suspected = True
                signals.append(
                    f"LSB steganography suspected: R={r_ratio:.3f} G={g_ratio:.3f} B={b_ratio:.3f} "
                    f"(deviations: {r_dev:.3f}, {g_dev:.3f}, {b_dev:.3f})"
                )
            elif any(d < 0.015 for d in [r_dev, g_dev, b_dev]):
                signals.append("LSB channel unusually uniform in one plane — low suspicion")

        except ImportError:
            signals.append("numpy not available — steganography check skipped")
        except Exception as e:
            print(f"[DOC-SCANNER] Stego analysis error: {e}")

        # ── Try to read text from image for URL extraction ────────────────────
        try:
            import pytesseract
            from PIL import Image
            img_pil = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(img_pil)
            urls = _extract_urls_from_text(text)
        except Exception:
            pass

        url_analysis = [_analyze_url(u) for u in urls]
        suspicious = [a["url"] for a in url_analysis if a["risk"] in ("HIGH", "MEDIUM")]
        return {
            "document_type": "image",
            "steganography_suspected": stego_suspected,
            "steganography_signals": signals,
            "urls_found": urls,
            "suspicious_urls": suspicious,
            "url_analysis": url_analysis,
            "embedded_files_found": False,
            "embedded_file_count": 0,
            "pdf_javascript_found": False,
            "pdf_auto_action_found": False,
        }

    def analyze_pdf(self, pdf_bytes: bytes) -> dict:
        """Analyze a PDF for embedded threats."""
        signals = []
        urls = []
        js_found = False
        auto_action = False
        embedded_files = False
        embedded_count = 0
        page_count = 0

        # Check for JavaScript & Auto-Action via raw byte signatures
        js_found = b"/JS" in pdf_bytes or b"/JavaScript" in pdf_bytes
        auto_action = b"/AA" in pdf_bytes or b"/OpenAction" in pdf_bytes

        # Attempt to use PyMuPDF first, fallback to pypdf
        doc_parsed = False
        full_text = ""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page_count = doc.page_count
            for page in doc:
                full_text += page.get_text() or ""
            embedded_count = doc.embfile_count()
            embedded_files = embedded_count > 0
            doc.close()
            doc_parsed = True
        except Exception as py_mupdf_err:
            print(f"[DOC-SCANNER] PyMuPDF not available or failed: {py_mupdf_err}. Falling back to pypdf.")

        if not doc_parsed:
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(pdf_bytes))
                page_count = len(reader.pages)
                for page in reader.pages:
                    full_text += page.extract_text() or ""
                
                # Check for embedded files via /Names /EmbeddedFiles
                try:
                    catalog = reader.trailer.get("/Root", {})
                    names = catalog.get("/Names", {})
                    emb_files = names.get("/EmbeddedFiles", {})
                    if emb_files:
                        embedded_count = len(emb_files.get("/Names", [])) // 2
                        embedded_files = embedded_count > 0
                except Exception:
                    pass
                
                doc_parsed = True
            except Exception as pypdf_err:
                signals.append(f"PDF parsing engine failure: {pypdf_err}")
                full_text = ""

        urls = _extract_urls_from_text(full_text)

        if js_found:
            signals.append("PDF contains JavaScript — execution risk")
        if auto_action:
            signals.append("PDF has auto-action triggers (/OpenAction or /AA)")
        if embedded_files:
            signals.append(f"PDF contains {embedded_count} embedded file(s)")

        url_analysis = [_analyze_url(u) for u in urls[:20]]
        suspicious = [a["url"] for a in url_analysis if a["risk"] in ("HIGH", "MEDIUM")]
        return {
            "document_type": "pdf",
            "page_count": page_count,
            "steganography_suspected": False,
            "steganography_signals": [],
            "urls_found": urls[:20],
            "suspicious_urls": suspicious[:10],
            "url_analysis": url_analysis,
            "embedded_files_found": embedded_files,
            "embedded_file_count": embedded_count,
            "pdf_javascript_found": js_found,
            "pdf_auto_action_found": auto_action,
        }
