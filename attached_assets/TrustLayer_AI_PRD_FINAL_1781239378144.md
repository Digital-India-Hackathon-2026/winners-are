# TrustLayer AI — Product Requirements Document
## Version 2.0 — Final Specification
**Product:** TrustLayer AI — India's First Payment Forensics Platform
**Team:** Hackfinity — WinnovX 2026
**Stack:** Next.js (Antigravity) · Supabase · Vercel · NVIDIA NIM APIs
**Deployed:** https://trust-layer-tool.vercel.app
**Last Updated:** June 2026

---

## 1. Product Vision

TrustLayer AI is India's first payment forensics platform — built to stop UPI payment fraud before it reaches the counter.

Every day, thousands of Indian merchants — kirana store owners, delivery agents, freelancers, and small businesses — lose money to fake UPI payment screenshots. A scammer sends a doctored receipt, pressures the merchant to release goods, and disappears. There is no official API to verify if a UPI transaction actually happened. Banks don't help. ChatGPT gives a vague answer. And the merchant has no tool.

TrustLayer fills that gap with a hybrid forensic engine: deterministic hard rules that catch lazy fakes instantly, combined with a multi-model NVIDIA NIM AI pipeline that catches sophisticated forgeries that rules alone would miss. Every digital artifact involved in a payment transaction — screenshots, QR codes, documents, images, and links — goes through TrustLayer before the merchant trusts it.

**Core Principle:** Hard rules run first, always. AI deepens and explains. Neither alone is enough.

---

## 2. Target Users

| User | Pain Point | How TrustLayer Helps |
|---|---|---|
| Kirana store owners | Receive fake PhonePe/GPay screenshots daily | Scan in 10 seconds before releasing goods |
| Street vendors & delivery agents | No time to verify, pressured by buyers | Instant HIGH/LOW risk verdict |
| E-commerce sellers | Accept UPI proof screenshots via WhatsApp | Batch verify before processing orders |
| Freelancers | Fake payment proofs for services already rendered | Verify before delivering work |
| Enterprise merchants | High volume payment verification at scale | Bulk API (Beta roadmap) |

---

## 3. Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Next.js via Antigravity (App Router) | Dark glassmorphism UI, cinematic scan animations, responsive |
| Backend | FastAPI (Python) | Core forensics engine, model orchestration, deterministic rules |
| Database & Auth | Supabase (Postgres + Edge Functions + Storage + Realtime) | Screenshot hashes, scan logs, fraud event registry |
| Deployment | Vercel | Auto-deploy from GitHub, zero-config CDN |
| Image Processing | Pillow + OpenCV + PyMuPDF | Pixel manipulation, EXIF parsing, QR decoding, PDF analysis |
| OCR Engine | NVIDIA Nemotron OCR v2 | Dedicated text extraction from receipts and documents |
| Visual AI | NVIDIA Nemotron Nano 12B v2 VL | Visual forensic reasoning, app recognition, layout analysis |
| Reasoning AI | Qwen 3.5-397B-A17B (MoE) | Forensic bullet generation, Trust Score synthesis |
| Deepfake AI | Hive Deepfake Image Detection (NVIDIA NIM) | AI-generated receipt detection |
| Safety AI | NVIDIA Nemotron Content Safety Reasoning 4B | Social engineering + pressure language detection |
| Guardrails | Meta Llama Guard 4-12B | Content safety guardrails across all model outputs |
| Fallback AI | Microsoft Phi-4-multimodal-instruct | Multimodal fallback when primary models fail |
| Phishing Check | Google Safe Browsing API (free tier) | URL threat detection |
| Malware Scan | VirusTotal API (free tier) | File and URL malware scanning |
| UPI Validation | Razorpay Sandbox API | Live VPA existence verification |

---

## 4. Product Features — Final Structure

TrustLayer v2.0 ships with **4 production features** and **1 beta feature.**

```
┌─────────────────────────────────────────────────────────────┐
│                     TRUSTLAYER AI v2.0                      │
├──────────────────────┬──────────────────────────────────────┤
│   PRODUCTION (Live)  │            BETA                      │
├──────────────────────┼──────────────────────────────────────┤
│ F1: Fake Screenshot  │ B1: WhatsApp Bot                     │
│     Detector         │     (forward screenshot →            │
│                      │      get verdict in 10 sec)          │
│ F2: QR Code Fraud    │                                      │
│     Inspector        │                                      │
│                      │                                      │
│ F3: Document &       │                                      │
│     Image Threat     │                                      │
│     Scanner +        │                                      │
│     URL Verifier     │                                      │
│                      │                                      │
│ F4: What To Do Next  │                                      │
└──────────────────────┴──────────────────────────────────────┘
```

---

## 5. Feature 1 — Fake Screenshot Detector

### Overview
The core product. A merchant uploads a UPI payment screenshot and receives a Trust Score (0–100) with a clear verdict and forensic explanation — in under 10 seconds. Internally, this is a 7-layer pipeline running simultaneously: deterministic rules, pixel forensics, OCR extraction, visual AI reasoning, deepfake detection, VPA live validation, and replay database lookup. The merchant sees none of this complexity — just the verdict.

### What Gets Checked (Internal Pipeline)

#### Layer 1 — Preprocessing & Integrity Checks (Deterministic)
Before any AI runs, hard rule violations are caught immediately. These checks are 100% deterministic — zero false positives, zero AI involvement.

- **Canvas Padding Removal:** Strips solid black/white borders added by scammers to manipulate aspect ratio detection or header color analysis. Cropped before any further processing.
- **File Integrity Check:** Validates file is a genuine image, not a renamed PDF, HTML, or script with an image extension.
- **Resolution Sanity Check:** Screenshots below 300×400px or above 8000×6000px are flagged — outside realistic device screenshot bounds.
- **Foreign Currency Hard Override:** Scans raw pixel text for any non-INR currency symbol (`$`, `€`, `£`, `USD`, `EUR`). UPI only handles Indian Rupees. Any foreign currency = instant HIGH RISK override. Trust Score drops to ≤10. No AI can reverse this.

#### Layer 2 — OCR Extraction (Nemotron OCR v2)
Nemotron OCR v2 runs a 3-component pipeline on the preprocessed image:

1. **Text Detector** (RegNetX-8GF convolutional backbone) — localizes all text regions with bounding boxes
2. **Text Recognizer** — transcribes text from each detected region with character-level confidence scores
3. **Relational Layout Model** — understands reading order, structural relationships between fields (amount vs label vs timestamp)

**Fields extracted with bounding box coordinates:**
- Transaction/UTR Reference Number
- UPI VPA (Payer and Recipient)
- Transaction Amount (₹)
- Timestamp (date + time)
- Merchant/Recipient Name
- Payment App Name (as printed in screenshot)
- Transaction Status text ("Payment Successful", "₹ Sent", etc.)

**Why Nemotron OCR v2 over a general VLM for extraction:**
General vision-language models like the old Nemotron-VL-8B perform OCR as a secondary capability. Nemotron OCR v2 is purpose-built for it — it has a dedicated detector, recognizer, and layout model trained on millions of real-world receipt and document images. For structured fields like UTR numbers, VPA addresses, and amounts, accuracy is significantly higher. A misread UTR digit means a missed fraud signal. This matters.

#### Layer 3 — Deterministic Rule Engine (Zero AI, Maximum Precision)
Running on the extracted fields — pure Python logic, no model inference:

- **UTR Format Validation:**
  - Must be exactly 12 digits
  - Must be numeric only (no letters, no spaces, no special chars)
  - Must not be a known dummy pattern (all same digits: 111111111111, sequential: 123456789012)
  - Violation: Trust Score hard drops to ≤15. HIGH RISK. Cannot be overridden by AI.

- **UPI VPA Format Validation:**
  - Must match `localpart@provider` pattern
  - Local part must be 3–50 characters, alphanumeric or dots/hyphens only
  - Provider handle must exist in known legitimate handle registry (see Section 8)
  - Unknown or misspelled handle → flag (e.g., `@phonepay` instead of `@ybl`)

- **Timestamp Logic Checks:**
  - Future timestamp → instant flag
  - Timestamp day-of-week inconsistency (e.g., screenshot says "Monday 15 Aug" but 15 Aug was a Sunday) → flag
  - Timestamp time format mismatch vs detected app (PhonePe: 12hr AM/PM, YONO SBI: 24hr, HDFC: DD/MM/YY) → flag
  - Transactions between 2:00 AM–4:00 AM → soft warning (statistically rare for merchant payments)

- **Amount Plausibility:**
  - Amount must be a positive number
  - Amount of exactly ₹0.00 or ₹0.01 (test transactions) → flag
  - Amount with more than 2 decimal places → flag (UPI amounts are always in paise at most)

#### Layer 4 — Visual Forensic Reasoning (Nemotron Nano 12B v2 VL)
The visual AI runs 4 parallel reasoning tasks on the full screenshot:

**Task A — Payment App Identification & Branding Verification:**
The model identifies which UPI app generated this screenshot by analyzing branding elements — logo, header bar, color scheme, typography, iconography, and layout structure. This is cross-validated against a deterministic hex color fingerprint:

| App | Primary Brand Hex | Secondary Validation |
|---|---|---|
| PhonePe | `#5f259f` (purple) | Confetti animation pattern, checkmark style |
| Google Pay | `#4285f4` (blue) + Material Design | Clean card layout, "Google Pay" wordmark |
| Paytm | `#00baf2` (cyan) | Banner header style, Paytm logo position |
| BHIM | `#004C8F` (dark blue) | NPCI branding, BHIM wordmark |
| Amazon Pay | `#FF9900` (orange) | Amazon smile logo, Amazon Pay header |
| FamPay | `#FFCC00` (yellow) | Youth-focused dark card layout |
| CRED | Dark glassmorphic | CRED logo, dark mode default |
| Navi | `#84CC16` (lime) | Navi wordmark, clean minimal layout |
| YONO SBI | `#1B3F7A` (dark blue) | SBI logo, YONO branding, formal layout |
| HDFC iMobile | `#004C8F` + red accent | HDFC eagle logo |
| ICICI iMobile | `#F7941D` (orange) | ICICI Bank wordmark |
| Kotak | `#E63B2E` (red) | Kotak wordmark, red accent |
| super.money | Neon green Flipkart-group | Flipkart group branding |
| Pop UPI | Orange success gradient | Pop wordmark |
| MobiKwik | `#2E86AB` | MobiKwik ZIP branding |

**Dual-validation rule:** Visual model identifies app AND hex color confirms it. If they disagree — flag as branding mismatch. A scammer using PhonePe's layout with the wrong purple shade fails both checks.

**Task B — Tampered Amount Detection:**
Pillow crops the amount field using Nemotron OCR v2 bounding box coordinates. The cropped region is sent to Nemotron Nano 12B v2 VL with a forensic prompt:
```
Analyze these amount digits for forensic tampering evidence.
Check: font weight consistency, kerning uniformity, anti-aliasing
sharpness, pixel density at digit edges vs surrounding text.
Answer: CONSISTENT or INCONSISTENT. One specific reason only.
```
Separately, pixel-level analysis checks standard deviation of edge density across all digit pixels — values outside expected range flag single-digit edits (₹450 → ₹4,500 is the most common scammer edit).

**Task C — Screenshot Authenticity Check:**
The model assesses whether the screenshot shows signs of being a genuine device capture or a fabricated image:
- Natural screen glare/reflection patterns present?
- Status bar (time, battery, signal) consistent with claimed timestamp?
- UI rendering artifacts consistent with real device anti-aliasing?
- Notification bar and system UI present and realistic?

**Task D — Layout Structure Consistency:**
Cross-checks that UI element positions, padding, margins, and structural relationships match known authentic templates for the identified app. Scammers replicating layouts often get spacing wrong by a few pixels.

#### Layer 5 — EXIF & Binary Metadata Forensics (Pillow + Custom Parser)
Deep scan of the raw image binary — no AI, pure deterministic analysis:

- **Software Tag Extraction:** Reads EXIF `Software`, `ProcessingSoftware`, `OriginalRawFileName` tags. Any mention of Photoshop, Canva, PicsArt, GIMP, Snapseed, Figma, LightRoom, PixelLab → flag with software name in output.
- **Creation vs Modification Timestamp Delta:** If EXIF creation date ≠ modification date → image was edited after capture.
- **Compression Profile Analysis:** Detects pixel compression clusters inconsistent with direct screenshot saves. Screenshot compression profiles differ from re-saved edited images.
- **Comment/IPTC/XMP Block Scan:** Scans all metadata text chunks for script-like strings (`<script>`, `eval(`, base64 blobs) — signals malware embedded in image metadata.
- **File Size Anomaly:** Cross-checks file size against resolution. Unusually large files for their pixel count signal hidden steganographic payloads.
- **ICC Profile Consistency:** Authentic phone screenshots use device-native ICC profiles. Edited images often carry Photoshop or Canva ICC profiles.

#### Layer 6 — Deepfake / AI-Generated Receipt Detection (Hive NIM)
Runs in parallel with Layer 4. Sends the full image to Hive's Deepfake Image Detection model on NVIDIA NIM:

- Returns a confidence score (0.0–1.0): 0 = genuine, 1 = AI-generated/deepfake
- Score > 0.70 → flag as AI-GENERATED, append to verdict
- Catches receipts generated by DALL-E, Stable Diffusion, Midjourney, or custom GAN models
- This catches the next generation of fraud that pixel editing detection entirely misses

```python
def check_deepfake(image_b64: str) -> dict:
    response = requests.post(
        "https://integrate.api.nvidia.com/v1/infer",
        headers={"Authorization": f"Bearer {NVIDIA_API_KEY}"},
        json={"input": [f"data:image/jpeg;base64,{image_b64}"]}
    )
    score = response.json()["data"][0]["score"]
    return {
        "is_deepfake": score > 0.70,
        "confidence_pct": round(score * 100, 1),
        "verdict": "AI_GENERATED" if score > 0.70 else "AUTHENTIC_CAPTURE"
    }
```

#### Layer 7 — Razorpay VPA Live Validation
Calls Razorpay's VPA validation API to confirm the UPI ID extracted from the screenshot actually exists as a registered, active account in the UPI network:

```python
import razorpay
client = razorpay.Client(auth=("rzp_test_key", "rzp_test_secret"))

def validate_vpa(vpa: str) -> dict:
    try:
        result = client.payment.validateVpa({"vpa": vpa})
        return {
            "exists": result.get("success", False),
            "registered_name": result.get("customer_name", "Unknown")
        }
    except Exception as e:
        return {"exists": None, "skipped": True, "reason": str(e)}
```

If the VPA does not exist → the payment never happened from that account. Instant HIGH RISK.
If VPA exists but registered name doesn't match screenshot name → flag as identity mismatch.

#### Layer 8 — Screenshot Replay / Reuse Detection (Supabase pHash)
Every uploaded screenshot gets a perceptual hash (pHash) generated via the `imagehash` library. This hash is checked against the Supabase `screenshot_hashes` table for near-duplicate matches (Hamming distance ≤ 8):

- **Exact match with prior HIGH RISK verdict:** Instant escalation — "This exact screenshot has been flagged X times. First seen Y days ago."
- **Near-duplicate match:** Soft flag — "A near-identical screenshot was previously flagged."
- **No match:** Store hash with current verdict for future lookups.

This creates a collective fraud intelligence network — every TrustLayer scan makes the system smarter for every future merchant.

#### Layer 9 — AI Forensic Synthesis (Qwen 3.5-397B MoE)
After all layers complete, Qwen 3.5-397B synthesizes all signals into a final verdict:

**Trust Score Weighting:**
```
UTR format valid                    : +25 points
VPA exists (Razorpay confirmed)     : +20 points
App branding matches (dual check)   : +15 points
EXIF clean (no editing software)    : +15 points
Deepfake score < 0.3                : +10 points
Timestamp consistent                : +8 points
Amount field consistent             : +7 points
No replay match                     : bonus +5 points if hash is new

Hard overrides (instant violations):
Foreign currency detected           : Score = max 10
UTR wrong format                    : Score = max 15
VPA does not exist                  : Score = max 20
Deepfake score > 0.70               : Score = max 25
EXIF shows editing software         : Score = max 40
```

**Forensic Bullets Prompt (Qwen 3.5-397B):**
```
You are a senior UPI payment forensics expert giving evidence to a court.
Given these scan results: {all_layer_outputs}
Generate EXACTLY 3 forensic findings. Rules:
- Each finding is ONE sentence only
- Reference actual extracted values (e.g., specific hex codes, exact UTR, software names)
- Never use vague language like "looks suspicious" or "appears fake"
- Be specific: "UTR '45357172' contains 8 digits; valid Indian UPI reference numbers
  are always exactly 12 digits per NPCI specification."
Return only a valid JSON array: ["finding1", "finding2", "finding3"]
```

**Verdict Classification:**
```
85–100  : ✅ LIKELY AUTHENTIC — Proceed with confidence
60–84   : ⚠️  SUSPICIOUS — Verify before proceeding
0–59    : 🚨 HIGH RISK — Do not release goods
```

---

## 6. Feature 2 — QR Code Fraud Inspector

### Overview
Scammers increasingly embed QR codes in fake payment screenshots — either pointing to a different UPI ID than the one shown in the text, or linking to phishing sites. This feature decodes any QR code visible in the uploaded screenshot and runs two validation checks on it.

### Check A — UPI ID Consistency Validation
```python
import cv2
from pyzbar.pyzbar import decode

def extract_qr_from_screenshot(image_path: str) -> dict:
    img = cv2.imread(image_path)
    decoded = decode(img)
    results = []
    for obj in decoded:
        raw = obj.data.decode("utf-8")
        results.append({
            "raw_data": raw,
            "type": obj.type,
            "is_upi": raw.startswith("upi://")
        })
    return results

def validate_upi_qr(qr_data: str, ocr_recipient: str) -> dict:
    # Parse: upi://pay?pa=merchant@ybl&pn=MerchantName&am=500&tr=UTR123
    params = dict(p.split("=") for p in qr_data.split("?")[1].split("&"))
    qr_vpa = params.get("pa", "").lower()
    qr_amount = params.get("am", "")
    qr_utr = params.get("tr", "")

    return {
        "qr_vpa": qr_vpa,
        "screenshot_vpa": ocr_recipient,
        "vpa_match": qr_vpa == ocr_recipient.lower(),
        "qr_amount": qr_amount,
        "qr_utr": qr_utr,
        "mismatch_detected": qr_vpa != ocr_recipient.lower()
    }
```

If the QR VPA ≠ OCR-extracted recipient VPA → the QR was designed to redirect payment to a different account than what the screenshot text claims.

### Check B — Phishing URL Detection
If the QR contains a URL (not a UPI deep link), it is immediately checked against Google Safe Browsing:

```python
def check_url_phishing(url: str) -> dict:
    response = requests.post(
        "https://safebrowsing.googleapis.com/v4/threatMatches:find",
        params={"key": GOOGLE_SAFE_BROWSING_KEY},
        json={
            "client": {"clientId": "trustlayer-ai", "clientVersion": "2.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }
    )
    matches = response.json().get("matches", [])
    return {
        "safe": len(matches) == 0,
        "threat_count": len(matches),
        "threat_types": [m["threatType"] for m in matches]
    }
```

**Output in UI:**
```
QR Code Found in Screenshot
├── Encoded VPA : fraud_account@paytm
├── Screenshot VPA: legit_merchant@ybl
├── VPA Match    : ❌ MISMATCH — QR redirects to different account
└── URL Safety   : 🚨 PHISHING DETECTED (SOCIAL_ENGINEERING)
```

---

## 7. Feature 3 — Document & Image Threat Scanner + URL Verifier

### Overview
TrustLayer extends beyond UPI screenshots to scan any digital artifact a scammer might send — bank statement PDFs, invoice images, payment confirmation JPGs, doctored bank letters. Every file gets scanned for tampering, malware, phishing links, and embedded threats. Every URL found in the file is verified. This makes TrustLayer the single tool a merchant needs for all payment-related documents.

### Accepted Formats
PNG, JPG, JPEG, WEBP, PDF, HEIC

### Sub-Feature 3A — Image Forensics
Same EXIF + metadata pipeline as Feature 1, applied to any image (not just UPI screenshots). Includes:
- Editing software detection in EXIF
- Steganographic payload detection (LSB analysis via Pillow)
- File size anomaly detection
- Hive deepfake detection on the image
- Nemotron Nano 12B v2 VL visual analysis for signs of digital manipulation

### Sub-Feature 3B — PDF / Document Analysis (PyMuPDF)
```python
import fitz  # PyMuPDF

def analyze_pdf(filepath: str) -> dict:
    doc = fitz.open(filepath)
    findings = []

    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        fonts_on_page = set()

        for block in blocks:
            if block["type"] == 0:  # Text block
                for line in block["lines"]:
                    for span in line["spans"]:
                        fonts_on_page.add(span["font"])
                        # Invisible text detection
                        if span["color"] == 16777215:  # Pure white
                            findings.append({
                                "type": "INVISIBLE_TEXT",
                                "page": page_num + 1,
                                "detail": "White text on white background detected"
                            })
                        # Micro text detection (hidden instructions)
                        if span["size"] < 2:
                            findings.append({
                                "type": "MICRO_TEXT",
                                "page": page_num + 1,
                                "detail": f"Text size {span['size']}pt — below visible threshold"
                            })

        # Font diversity check — legitimate bank PDFs use 1-3 fonts
        if len(fonts_on_page) > 5:
            findings.append({
                "type": "FONT_DIVERSITY",
                "page": page_num + 1,
                "detail": f"{len(fonts_on_page)} different fonts — indicates copy-paste tampering"
            })

    # Metadata analysis
    metadata = doc.metadata
    editing_tools = ["canva", "photoshop", "gimp", "picsart", "figma", "pixelmator"]
    producer = (metadata.get("producer") or "").lower()
    creator = (metadata.get("creator") or "").lower()

    for tool in editing_tools:
        if tool in producer or tool in creator:
            findings.append({
                "type": "EDITING_SOFTWARE",
                "detail": f"Document produced by {tool} — not a bank or financial system"
            })

    # Overlapping object detection (element replacement)
    for page_num, page in enumerate(doc):
        paths = page.get_drawings()
        if len(paths) > 100:
            findings.append({
                "type": "ELEMENT_OVERLAY",
                "page": page_num + 1,
                "detail": f"{len(paths)} drawing objects — possible element replacement"
            })

    doc.close()
    return {
        "findings": findings,
        "risk_level": "HIGH" if len(findings) > 2 else "MEDIUM" if findings else "LOW",
        "finding_count": len(findings)
    }
```

### Sub-Feature 3C — URL Verifier (Core Addition)
Every URL found in an uploaded document or image is extracted, validated, and threat-checked. This is a complete URL intelligence pipeline:

**Step 1 — URL Extraction:**
```python
import re

def extract_all_urls(text: str) -> list:
    # Standard URL pattern
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)

    # Also extract bare domains that look suspicious
    domain_pattern = r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,}\b'
    bare_domains = re.findall(domain_pattern, text.lower())

    # Detect shortened URLs
    shorteners = ["bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly",
                  "shorturl.at", "rebrand.ly", "cutt.ly", "tiny.cc"]
    shortened = [u for u in urls if any(s in u for s in shorteners)]

    return {
        "all_urls": list(set(urls)),
        "shortened_urls": shortened,
        "bare_domains": bare_domains
    }
```

**Step 2 — Google Safe Browsing Batch Check:**
```python
def batch_check_urls(urls: list) -> dict:
    if not urls:
        return {"results": []}

    response = requests.post(
        "https://safebrowsing.googleapis.com/v4/threatMatches:find",
        params={"key": GOOGLE_SAFE_BROWSING_KEY},
        json={
            "client": {"clientId": "trustlayer-ai", "clientVersion": "2.0"},
            "threatInfo": {
                "threatTypes": [
                    "MALWARE",
                    "SOCIAL_ENGINEERING",
                    "UNWANTED_SOFTWARE",
                    "POTENTIALLY_HARMFUL_APPLICATION"
                ],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": u} for u in urls]
            }
        }
    )
    threat_urls = {m["threat"]["url"] for m in response.json().get("matches", [])}
    return [
        {
            "url": u,
            "safe": u not in threat_urls,
            "shortened": any(s in u for s in ["bit.ly", "tinyurl", "t.co", "goo.gl"]),
            "status": "🚨 PHISHING" if u in threat_urls else "⚠️ SHORTENED" if any(s in u for s in ["bit.ly", "tinyurl"]) else "✅ SAFE"
        }
        for u in urls
    ]
```

**Step 3 — VirusTotal File Scan (for uploaded documents):**
```python
import vt

def scan_file_virustotal(filepath: str) -> dict:
    client = vt.Client(VIRUSTOTAL_API_KEY)
    try:
        with open(filepath, "rb") as f:
            analysis = client.scan_file(f, wait_for_completion=True)
        stats = analysis.stats
        return {
            "malicious": stats.get("malicious", 0),
            "suspicious": stats.get("suspicious", 0),
            "harmless": stats.get("harmless", 0),
            "verdict": "MALWARE" if stats.get("malicious", 0) > 0 else
                       "SUSPICIOUS" if stats.get("suspicious", 0) > 2 else "CLEAN"
        }
    finally:
        client.close()
```

**Step 4 — Shortened URL Resolver:**
All shortened URLs are resolved to their final destination before checking:
```python
def resolve_shortened_url(url: str) -> str:
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.url  # Final destination after all redirects
    except:
        return url
```

**URL Verifier Output in UI:**
```
URLs Found in Document: 4

✅ https://sbi.co.in                    Safe
🚨 https://sbi-kyc-verify.xyz          PHISHING — Social Engineering
⚠️  https://bit.ly/x7Kp2q              Shortened → resolves to malware.ru → MALWARE
⚠️  https://secure-upi-verify.in       Suspicious domain — not a registered bank domain

Document File Scan (VirusTotal):
Malicious detections: 3/72 engines
Verdict: 🚨 MALWARE DETECTED
```

### Sub-Feature 3D — Steganographic Payload Detection
Images often carry hidden data in pixel LSBs — invisible to the eye, detectable by analysis:

```python
from PIL import Image
import numpy as np

def detect_steganography(image_path: str) -> dict:
    img = Image.open(image_path).convert("RGB")
    pixels = np.array(img)

    # Extract LSBs from all channels
    lsb_r = pixels[:,:,0] & 1
    lsb_g = pixels[:,:,1] & 1
    lsb_b = pixels[:,:,2] & 1

    # Calculate entropy of LSB plane
    lsb_flat = np.concatenate([lsb_r.flatten(), lsb_g.flatten(), lsb_b.flatten()])
    entropy = -np.sum(
        np.unique(lsb_flat, return_counts=True)[1] / len(lsb_flat) *
        np.log2(np.unique(lsb_flat, return_counts=True)[1] / len(lsb_flat) + 1e-10)
    )

    # Natural images: LSB entropy ~0.9-1.0 (near random)
    # Steganographic images: LSB entropy closer to 1.0 with unusual patterns
    suspicious = entropy > 0.98 and pixels.std() < 30
    return {
        "lsb_entropy": round(float(entropy), 4),
        "steganography_suspected": suspicious,
        "detail": "Anomalous LSB entropy pattern — possible hidden payload" if suspicious else "LSB pattern normal"
    }
```

---

## 8. Feature 4 — What To Do Next

### Overview
Detection without guidance is incomplete. After every scan, TrustLayer tells the merchant exactly what action to take — specific, plain-language, practical steps based on the specific risk level and fraud type detected. This is generated by Qwen 3.5-397B based on the fraud signals found.

### Verdict-Based Guidance

**🚨 HIGH RISK — Fake Payment Detected**
```
Do NOT release goods or services yet.

Immediate steps:
1. Tell the customer the payment is not showing on your end
2. Ask them to show you live bank balance or transaction history on their phone
3. Request fresh payment — cash, or a new UPI transfer initiated in front of you
4. Screenshot and save this fake receipt as evidence
5. If the customer becomes aggressive, note their phone number and description

If significant amount:
→ File a cybercrime complaint at cybercrime.gov.in or call 1930
→ Report the UPI ID to NPCI via your bank app
```

**⚠️ SUSPICIOUS — Needs Manual Verification**
```
Hold delivery temporarily.

Verification steps:
1. Check your own bank app or UPI app — does the credit appear?
2. Wait 5–10 minutes — some transactions take time to reflect
3. Ask customer to share the bank SMS confirmation (not screenshot — actual SMS)
4. Call your bank helpline to confirm if credit is processing

If credit doesn't appear in 15 minutes:
→ The payment likely did not go through
→ Request fresh payment before proceeding
```

**✅ LIKELY AUTHENTIC — Proceed**
```
Transaction appears legitimate.

Recommended steps:
1. Verify the credited amount matches the purchase total
2. Proceed with confidence
3. Save this TrustLayer scan result as your digital payment record
4. If any doubt remains, wait 2 minutes for bank SMS confirmation
```

### Dynamic "What To Do Next" Generation
For nuanced cases, Qwen 3.5-397B generates context-specific guidance:

```python
WHAT_TO_DO_PROMPT = """
You are a payment fraud advisor for Indian small merchants.
A merchant just received this scan result:
- Trust Score: {trust_score}
- Risk Level: {risk_level}  
- Fraud Signals Found: {signals}
- App Detected: {app_name}
- Amount Claimed: {amount}

Write a 'What To Do Next' guide for this specific merchant.
Rules:
- Use simple English, no jargon
- Maximum 5 bullet points
- Be specific to the fraud type detected
- Include the national cybercrime helpline (1930) if score < 40
- First line must be a single bold action sentence
Return as JSON: {"action_headline": "...", "steps": ["step1", "step2", ...]}
"""
```

---

## 9. Beta Feature — WhatsApp Bot (B1)

### Overview
The single beta feature. The most impactful distribution channel for TrustLayer in real India. A kirana store owner in a Tier-3 city is not opening a web app. He is on WhatsApp. He receives a fake payment screenshot on WhatsApp. He should be able to forward it to TrustLayer — and get a verdict in 10 seconds, in the same app, without friction.

### Architecture
```
Merchant receives fake screenshot on WhatsApp
              ↓
Forwards to TrustLayer WhatsApp Business number
              ↓
Meta WhatsApp Business API webhook → Supabase Edge Function
              ↓
Edge Function downloads image, calls FastAPI forensic pipeline
              ↓
Full 7-layer scan runs (same as Feature 1)
              ↓
Verdict formatted as WhatsApp message
              ↓
Merchant receives result in ~10 seconds
```

### Sample Bot Response
```
TrustLayer AI 🔍
━━━━━━━━━━━━━━━━━━━
Trust Score: 18 / 100
Verdict: 🚨 HIGH RISK — Likely Fake

Findings:
• UTR '45357172' has 8 digits — must be 12
• Header color doesn't match real PhonePe
• Image edited in Canva 2.0 (found in metadata)
• This screenshot was flagged 3× before

What to do:
⛔ Do NOT release goods
📱 Ask for cash or fresh payment
📞 If pressured, call 1930
━━━━━━━━━━━━━━━━━━━
Powered by TrustLayer AI
```

### Tech Required
- Meta WhatsApp Business API (1,000 free conversations/month)
- OR Twilio WhatsApp Sandbox (easier dev setup)
- Supabase Edge Function as webhook receiver
- Existing FastAPI pipeline unchanged

---

## 10. NVIDIA NIM Model Architecture

### Why Dual-Model Image Pipeline

TrustLayer uses two separate models for image analysis rather than one — because no single model is best at both tasks:

| Task | Dedicated Model | Why Separate |
|---|---|---|
| Text Extraction | Nemotron OCR v2 | 3-component architecture purpose-built for OCR. Character-level accuracy on structured receipt fields. A misread UTR digit = missed fraud. |
| Visual Reasoning | Nemotron Nano 12B v2 VL | Trained on invoices/receipts/manuals. Leads OCRBench v2. 128K context. 35% faster than VL-8B. Understands visual layout, not just text. |

Using a general VLM for both is a compromise. TrustLayer uses the right tool for each job.

### Model Assignment Table

| Role | Model ID | Version Upgraded From | Reason |
|---|---|---|---|
| Text Extraction | `nvidia/nemotron-ocr-v2` | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | Dedicated OCR: detector + recognizer + layout model. Far more accurate on structured receipt fields. |
| Visual Forensic Reasoning | `nvidia/nemotron-nano-12b-v2-vl` | `nvidia/llama-3.1-nemotron-nano-vl-8b-v1` | Leads OCRBench v2. Built for invoices & receipts. 128K context. 35% faster. |
| Forensic Bullet Generation | `qwen/qwen3.5-397b-a17b` | `qwen/qwen3.5-122b-a10b` | Next-gen MoE 397B. Stronger reasoning. Better forensic precision. |
| Deepfake Detection | `hive/deepfake-image-detection` | *(Was Beta — not available)* | Now on NVIDIA NIM. Promoted to Production. |
| Pressure Language / Safety | `nvidia/nemotron-content-safety-reasoning-4b` | `qwen` generic prompt | Purpose-built context-aware safety reasoning. Domain policy enforcement. |
| Multimodal Fallback | `microsoft/phi-4-multimodal-instruct` | `microsoft/phi-4-mini-instruct` (text-only) | Now sees screenshots when primary models fail. Critical upgrade. |
| Content Guardrails | `meta/llama-guard-4-12b` | No change | Best-in-class multilingual safety guardrails. ✅ |

### Full Scan Pipeline

```
Input: Image / PDF / Document
         │
         ▼
┌─────────────────────────────────┐
│  PREPROCESSING (Deterministic)  │
│  Canvas crop, file validation,  │
│  foreign currency hard override  │
└────────────┬────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────┐
│              PARALLEL EXECUTION (All run simultaneously)    │
├──────────────────┬──────────────────┬──────────────────────┤
│ nemotron-ocr-v2  │ nemotron-nano-   │ hive/deepfake-       │
│                  │ 12b-v2-vl        │ image-detection      │
│ Extract:         │                  │                      │
│ • UTR            │ Verify:          │ Detect:              │
│ • VPA            │ • App branding   │ • AI-generated       │
│ • Amount         │ • Layout struct  │   receipt            │
│ • Timestamp      │ • Amount pixels  │ • Confidence score   │
│ • App name       │ • Authenticity   │                      │
│ • Merchant name  │                  │                      │
└──────────────────┴──────────────────┴──────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│           DETERMINISTIC RULES ENGINE                         │
│  UTR format • VPA handle registry • Timestamp logic          │
│  Amount plausibility • Razorpay VPA live check               │
│  pHash replay lookup (Supabase)                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  qwen3.5-397b-a17b   │
              │  • Synthesize all    │
              │    layer outputs     │
              │  • Generate 3        │
              │    forensic bullets  │
              │  • Calculate final   │
              │    Trust Score       │
              └──────────┬───────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │  meta/llama-guard-   │
              │  4-12b               │
              │  Content safety      │
              │  check on output     │
              └──────────┬───────────┘
                         │
                         ▼
         ┌───────────────────────────────┐
         │  Trust Score + Verdict +      │
         │  3 Forensic Bullets +         │
         │  What To Do Next → UI         │
         └───────────────────────────────┘
                         │
              (If any model fails)
                         │
                         ▼
         ┌───────────────────────────────┐
         │  microsoft/phi-4-multimodal   │
         │  Fallback — still sees the    │
         │  screenshot, not blind        │
         └───────────────────────────────┘
```

**Base URL:** `https://integrate.api.nvidia.com/v1`
**Auth:** `Authorization: Bearer {NVIDIA_API_KEY}`
**Protocol:** OpenAI-compatible `POST /v1/chat/completions`

---

## 11. Supabase Database Schema

```sql
-- Merchants
CREATE TABLE merchants (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  phone       TEXT UNIQUE,
  name        TEXT,
  city        TEXT,
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Scans (one row per scan)
CREATE TABLE scans (
  id                  UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  merchant_id         UUID REFERENCES merchants(id),
  timestamp           TIMESTAMPTZ DEFAULT NOW(),
  scan_type           TEXT CHECK (scan_type IN ('SCREENSHOT','DOCUMENT','IMAGE','QR')),
  trust_score         INTEGER CHECK (trust_score BETWEEN 0 AND 100),
  verdict             TEXT CHECK (verdict IN ('LIKELY_FAKE','SUSPICIOUS','LIKELY_AUTHENTIC')),
  risk_level          TEXT CHECK (risk_level IN ('HIGH','MEDIUM','LOW')),
  app_detected        TEXT,
  utr_extracted       TEXT,
  vpa_extracted       TEXT,
  amount_extracted    NUMERIC(12,2),
  timestamp_extracted TEXT,
  flags               JSONB,
  ai_bullets          JSONB,
  what_to_do_next     JSONB,
  processing_ms       INTEGER,
  city                TEXT
);

-- Screenshot hash registry (replay detection)
CREATE TABLE screenshot_hashes (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  phash       TEXT NOT NULL,
  verdict     TEXT,
  risk_level  TEXT,
  flag_count  INTEGER DEFAULT 1,
  first_seen  TIMESTAMPTZ DEFAULT NOW(),
  last_seen   TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_phash ON screenshot_hashes (phash);

-- Fraud events (individual signal log per scan)
CREATE TABLE fraud_events (
  id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scan_id     UUID REFERENCES scans(id),
  event_type  TEXT,  -- 'UTR_INVALID', 'EXIF_TAMPERING', 'DEEPFAKE', etc.
  detail      TEXT,
  severity    TEXT CHECK (severity IN ('HIGH','MEDIUM','LOW','INFO')),
  layer       TEXT,  -- which pipeline layer caught it
  detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Known fake template registry
CREATE TABLE fake_templates (
  id                UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  app_name          TEXT,
  template_version  TEXT,
  color_profile     JSONB,
  layout_signature  TEXT,
  match_count       INTEGER DEFAULT 0,
  added_at          TIMESTAMPTZ DEFAULT NOW()
);

-- URL scan results
CREATE TABLE url_scans (
  id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  scan_id         UUID REFERENCES scans(id),
  url             TEXT,
  resolved_url    TEXT,
  is_shortened    BOOLEAN DEFAULT FALSE,
  safe_browsing   TEXT CHECK (safe_browsing IN ('SAFE','PHISHING','MALWARE','SUSPICIOUS')),
  virustotal      TEXT,
  scanned_at      TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 12. UPI VPA Handle Registry

```python
VALID_UPI_HANDLES = {
    # Google Pay
    "@oksbi"        : "State Bank of India (Google Pay)",
    "@okaxis"       : "Axis Bank (Google Pay)",
    "@okhdfcbank"   : "HDFC Bank (Google Pay)",
    "@okicici"      : "ICICI Bank (Google Pay)",
    # PhonePe
    "@ybl"          : "Yes Bank (PhonePe)",
    "@ibl"          : "IDBI Bank (PhonePe)",
    "@axl"          : "Axis Bank (PhonePe)",
    # Paytm
    "@paytm"        : "Paytm Payments Bank",
    # Amazon Pay
    "@apl"          : "Amazon Pay (Axis Bank)",
    # BHIM / NPCI
    "@upi"          : "BHIM UPI",
    "@rbl"          : "RBL Bank",
    # Others
    "@fam"          : "FamPay (Federal Bank)",
    "@naviaxis"     : "Navi (Axis Bank)",
    "@axisb"        : "Axis Bank Direct",
    "@icici"        : "ICICI Bank Direct",
    "@sbi"          : "SBI Direct",
    "@hdfcbank"     : "HDFC Bank Direct",
    "@kotak"        : "Kotak Mahindra Bank",
    "@indus"        : "IndusInd Bank",
    "@rapl"         : "Reliance Jio (Axis)",
    "@mbk"          : "MobiKwik",
    "@cred"         : "CRED (Federal Bank)",
    "@freecharge"   : "Freecharge (Axis Bank)",
    "@Sliceaxis"    : "Slice (Axis Bank)",
    "@pockets"      : "ICICI Pockets",
    "@idfc"         : "IDFC First Bank",
    "@ikwik"        : "MobiKwik (IDBI)",
    "@superyes"     : "super.money (Yes Bank)",
    "@barodampay"   : "Bank of Baroda",
    "@cnrb"         : "Canara Bank",
    "@unionbank"    : "Union Bank of India",
    "@pnb"          : "Punjab National Bank",
}

def validate_upi_handle(vpa: str) -> dict:
    handle = "@" + vpa.split("@")[-1].lower().strip()
    if handle in VALID_UPI_HANDLES:
        return {"valid": True, "bank": VALID_UPI_HANDLES[handle]}
    return {
        "valid": False,
        "bank": None,
        "flag": f"Unknown UPI handle: {handle} — not in NPCI registered provider list"
    }
```

---

## 13. WinnovX 2026 — Jury Criteria Mapping

| Criterion | TrustLayer Response |
|---|---|
| **Problem Understanding** | India's ₹14,000 Cr UPI fraud crisis. Merchants have zero tools. Banks don't verify. ChatGPT guesses. TrustLayer forensics. |
| **Innovation & Originality** | Only team at WinnovX doing payment forensics. Zero direct competition in this hackathon. |
| **Technical Approach** | Hybrid deterministic + 7-layer multi-model AI pipeline. Not an LLM wrapper. Hard rules + AI reasoning together. |
| **Prototype Functionality** | Live deployed product at trust-layer-tool.vercel.app. Demo-able in the room. |
| **Technical Complexity** | Dual NVIDIA NIM image pipeline (Nemotron OCR v2 + Nano 12B v2 VL) + Hive deepfake + Qwen 397B + pixel forensics + Supabase pHash network + Razorpay live API + VirusTotal + Google Safe Browsing |
| **Impact & Relevance** | Every kirana store, every street vendor, every small merchant in India. Tier 1 to Tier 3. |
| **Scalability & Future Scope** | WhatsApp Bot scales to 500M WhatsApp users in India with zero UI friction. |
| **User Experience** | Cinematic scan animation, glassmorphic dark UI, single-button verdict, Hindi fraud examples on landing page. |
| **Presentation** | Landing page tells the full story before you say a word. Live demo closes it. |
| **Jury Q&A** | See Section 14. |

---

## 14. Jury Q&A — Prepared Answers

**Q: Can't someone just use ChatGPT or Gemini for this?**
> "ChatGPT can look at a screenshot and say it looks suspicious — but it cannot enforce a deterministic 12-digit UTR rule with zero exceptions, scan raw binary EXIF headers for Canva signatures, call Razorpay's live API to check if a UPI ID actually exists, run a perceptual hash against a fraud database, or check a QR URL against Google Safe Browsing. General LLMs are probabilistic. They hallucinate. Our deterministic layer has zero tolerance — UTR wrong format means Trust Score ≤15, no AI override. That hybrid is the moat."

**Q: What's your accuracy?**
> "Our deterministic checks — UTR format, foreign currency detection, VPA handle validation — are 100% rule-based with zero false positives. These are mathematical checks, not AI opinions. Our AI layers add depth and catch sophisticated fakes the rules miss. We're logging every scan verdict in Supabase to build a ground truth dataset and measure accuracy over time."

**Q: What if a scammer uses a real screenshot from a different transaction?**
> "Three layers catch that. First, Razorpay VPA validation checks if the UPI ID matches the actual merchant. Second, the amount in the screenshot must match what was agreed — a real screenshot from a ₹200 transaction won't pass for ₹20,000. Third, our pHash replay database flags if that screenshot has been used to defraud someone else before. Real screenshot, wrong context — still caught."

**Q: Why won't merchants just call the bank?**
> "A kirana store owner doing 200 transactions a day cannot call his bank for each one. Banks put you on hold for 10 minutes. The scammer pressures the merchant for 30 seconds. TrustLayer gives a verdict in under 10 seconds — faster than any scammer can apply pressure."

**Q: How is this different from just looking at the screenshot carefully?**
> "The human eye cannot read raw binary EXIF headers. It cannot detect a 3-pixel font anti-aliasing inconsistency in an amount field. It cannot check if a UPI ID is registered in the network. It cannot recognize a perceptual hash match against a fraud database. TrustLayer does all of that simultaneously, in 10 seconds, every time, without fatigue."

**Q: What's your go-to-market?**
> "Phase 1 is the WhatsApp Bot — zero friction, zero download, zero learning curve. Merchants already live on WhatsApp. They forward the screenshot, they get the verdict. Phase 2 is a Razorpay merchant plugin — integrate into existing checkout flows. Phase 3 is a bulk API for e-commerce platforms and delivery apps. The product meets India where India already is."

---

## 15. Model Changelog — v1.0 → v2.0

| Role | v1.0 | v2.0 | Change |
|---|---|---|---|
| OCR / Text Extraction | `llama-3.1-nemotron-nano-vl-8b-v1` | `nemotron-ocr-v2` | Dedicated 3-component OCR. Far more accurate on receipts. |
| Visual Reasoning | `llama-3.1-nemotron-nano-vl-8b-v1` | `nemotron-nano-12b-v2-vl` | OCRBench v2 leader. 128K context. 35% faster. Receipt-native. |
| Forensic Reasoning | `qwen3.5-122b-a10b` | `qwen3.5-397b-a17b` | Next-gen MoE. Stronger reasoning quality. |
| Fallback | `phi-4-mini-instruct` (text-only) | `phi-4-multimodal-instruct` | Fallback now sees the screenshot. |
| Deepfake Detection | *(Beta — unavailable)* | `hive/deepfake-image-detection` | Promoted to Production. NVIDIA NIM. |
| Pressure Language | `qwen` generic prompt | `nemotron-content-safety-reasoning-4b` | Purpose-built safety reasoning. |
| Guardrails | `llama-guard-4-12b` | `llama-guard-4-12b` | No change. ✅ |

---

*TrustLayer AI — Build boldly. Verify everything.*
*Team Hackfinity — WinnovX 2026*
