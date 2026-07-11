"""Turns raw scan-pipeline JSON into a short, human WhatsApp message."""
import random
import re

EDUCATIONAL_TIPS = [
    "Remember: A screenshot is never proof of payment. Always verify inside your own banking app.",
    "Banks and payment apps never ask for your UPI PIN or OTP to receive money.",
    "Always check your account balance directly before handing over goods to a customer.",
    "Genuine helpline numbers are never personal mobile numbers. Report cyber fraud at 1930.",
    "Never click on links or download files sent by unknown numbers on WhatsApp."
]

def generate_whatsapp_response(
    risk_level: str,  # "Safe", "Be Careful", "High Risk"
    summary: str,
    what_we_found: dict,
    why_concerned: str,
    what_to_do: list,
    what_not_to_do: list,
    is_senior: bool = False,
    scam_type: str = "general"
) -> str:
    # Emojis for risk level
    risk_emoji = {
        "Safe": "🟢 Safe",
        "Be Careful": "🟡 Be Careful",
        "High Risk": "🔴 High Risk"
    }.get(risk_level, "⚪ Unknown")
    
    # Rotated safety tips
    tip = random.choice(EDUCATIONAL_TIPS)
    
    if is_senior:
        # Elderly Mode formatting:
        # - Very short sentences
        # - Large spacing (double newlines)
        # - Maximum one idea per line
        # - No abbreviations
        # - Calm language
        
        # Translate technical names to senior friendly
        friendly_found = {}
        for k, v in what_we_found.items():
            if not v:
                continue
            k_friendly = {
                "Amount": "Money Amount",
                "Receiver": "Person Receiving",
                "Phone": "Phone Number",
                "UPI ID": "Payment Address",
                "Transaction ID": "Reference Number",
                "Website": "Website Link",
                "QR Destination": "Pay Link",
                "Bank Name": "Bank Name",
                "Date": "Date",
                "Time": "Time",
                "Payment Status": "Payment Status",
                "Merchant": "Merchant Name",
                "Subject": "Subject Name",
                "Sender": "Sender Name"
            }.get(k, k)
            friendly_found[k_friendly] = v
            
        found_lines = []
        for k, v in friendly_found.items():
            found_lines.append(f"{k}: {v}")
        found_str = "\n\n".join(found_lines)
        
        todo_str = "\n\n".join([f"{i+1}. {act}" for i, act in enumerate(what_to_do)])
        notodo_str = "\n\n".join([f"• {act}" for act in what_not_to_do])
        
        lines = [
            "🛡 *TrustLayer Security Report*",
            "",
            "Is this safe?",
            risk_emoji,
            "",
            "Our answer:",
            summary,
            "",
            "Why we think this:",
            why_concerned,
        ]
        
        if found_str:
            lines += [
                "",
                "What we found in the file:",
                found_str
            ]
            
        lines += [
            "",
            "What you should do now:",
            todo_str,
            "",
            "What you must not do:",
            notodo_str
        ]
        
        if risk_level == "High Risk":
            involves_money = scam_type in (
                "Fake UPI Screenshot",
                "Fake QR Code",
                "Investment Scam",
                "Fake Bank Statement",
                "general"
            ) and "content policy" not in why_concerned.lower() and "suggestive" not in why_concerned.lower()

            lines += [
                "",
                "If you need urgent help:",
            ]
            if involves_money:
                lines.append("• Call your bank immediately if you sent money.")
            lines += [
                "• Call government safety helpers at 1930.",
                "• Report to website: cybercrime.gov.in"
            ]
            
        # Senior friendly educational tip translation
        senior_tips = {
            "Remember: A screenshot is never proof of payment. Always verify inside your own banking app.":
                "Always open your official bank app to check if money arrived.",
            "Banks and payment apps never ask for your UPI PIN or OTP to receive money.":
                "Never type your payment PIN to receive money.",
            "Always check your account balance directly before handing over goods to a customer.":
                "Check your balance directly inside your bank app before giving goods.",
            "Genuine helpline numbers are never personal mobile numbers. Report cyber fraud at 1930.":
                "Call the safe government safety helpers at 1930 if you are worried.",
            "Never click on links or download files sent by unknown numbers on WhatsApp.":
                "Never click links sent by unknown people."
        }
        friendly_tip = senior_tips.get(tip, tip)
        
        lines += [
            "",
            "Safety Tip for you:",
            friendly_tip
        ]
        
        return "\n\n".join(lines)
        
    else:
        # Standard WhatsApp Mode formatting:
        found_lines = []
        for k, v in what_we_found.items():
            if v:
                found_lines.append(f"{k}: {v}")
        found_str = "\n".join(found_lines)
        
        todo_str = "\n".join([f"{i+1}. {act}" for i, act in enumerate(what_to_do)])
        notodo_str = "\n".join([f"• {act}" for act in what_not_to_do])
        
        lines = [
            "🛡 *TrustLayer Result*",
            f"Risk: {risk_emoji}",
            "---------------------------------------",
            summary,
            "---------------------------------------",
        ]
        
        if found_str:
            lines += [
                "*What we found:*",
                found_str,
                "---------------------------------------",
            ]
            
        lines += [
            "*Why we think this:*",
            why_concerned,
            "---------------------------------------",
            "*What you should do now:*",
            todo_str,
            "---------------------------------------",
            "*What NOT to do:*",
            notodo_str,
        ]
        
        if risk_level == "High Risk":
            involves_money = scam_type in (
                "Fake UPI Screenshot",
                "Fake QR Code",
                "Investment Scam",
                "Fake Bank Statement",
                "general"
            ) and "content policy" not in why_concerned.lower() and "suggestive" not in why_concerned.lower()

            lines += [
                "---------------------------------------",
                "*Need urgent help?*",
            ]
            if involves_money:
                lines.append("• Call your bank immediately if money has already been transferred.")
            lines += [
                "• Call Cyber Crime Helpline 1930.",
                "• Report at cybercrime.gov.in"
            ]
            
        lines += [
            "---------------------------------------",
            f"💡 {tip}"
        ]
        
        return "\n".join(lines)


def format_screenshot_result(data: dict, is_senior: bool = False) -> str:
    ts = data.get("trust_score_data", {}) or {}
    ocr = (data.get("ocr_data", {}) or {}).get("fields", {}) or {}
    vpa = data.get("vpa_validation_data", {}) or {}
    deepfake = data.get("deepfake_data", {}) or {}
    app = data.get("app_forensics", {}) or {}
    raw_text = ((data.get("ocr_data", {}) or {}).get("raw_text", "") or "").lower()

    # Extract dynamic found variables
    amount = ocr.get("payment_amount") or ocr.get("amount")
    receiver = ocr.get("receiver_name") or vpa.get("registered_name")
    phone = ocr.get("phone")
    upi_id = vpa.get("upi_id") or ocr.get("upi_id")
    tx_id = ocr.get("upi_transaction_id") or ocr.get("transaction_reference")
    app_name = ocr.get("payment_app_name") or app.get("detected_app")
    
    date_val = None
    time_val = None
    timestamp = ocr.get("timestamp")
    if timestamp:
        if "," in timestamp:
            parts = timestamp.split(",")
            date_val = parts[0].strip()
            time_val = parts[1].strip()
        else:
            date_val = timestamp

    what_we_found = {
        "Amount": amount,
        "Receiver": receiver,
        "Phone": phone,
        "UPI ID": upi_id,
        "Transaction ID": tx_id,
        "Payment App": app_name,
        "Date": date_val,
        "Time": time_val
    }

    # Classify scam type
    is_df = deepfake.get("is_deepfake", False)
    risk_level = "High Risk" if ts.get("risk_level") == "HIGH" else "Be Careful" if ts.get("risk_level") == "MEDIUM" else "Safe"
    
    # Prioritize dynamic findings from the pipeline and translate technical jargon to layman terms
    reasons = ts.get("confidence_reasoning", [])
    if reasons:
        summary = ts.get("verdict") or {
            "High Risk": "We believe this payment proof is fake and not trustworthy.",
            "Be Careful": "We found suspicious signs in this payment proof.",
            "Safe": "We believe this payment proof is authentic and safe."
        }.get(risk_level, "Suspicious activity detected.")
        
        replacements = {
            "EXIF metadata": "hidden file history details",
            "EXIF": "file history",
            "metadata": "hidden file details",
            "steganography": "hidden text/images",
            "pHash": "visual layout fingerprint",
            "perceptual hash": "visual template",
            "VPA handle": "UPI address suffix",
            "VPA": "UPI payment ID",
            "Razorpay live check": "live payment network verification",
            "baseline alignment": "text spacing alignment check",
            "ELA": "digital editing compression test",
            "compression mismatch": "evidence of local editing",
            "authenticity check": "security template match"
        }
        
        # Compile a single regex matching word boundaries for any key, sorted by length descending
        sorted_keys = sorted(replacements.keys(), key=len, reverse=True)
        pattern = re.compile("|".join(r"\b{}\b".format(re.escape(k)) for k in sorted_keys), re.IGNORECASE)

        layman_reasons = []
        for r in reasons:
            lr = pattern.sub(lambda m: replacements[next(k for k in sorted_keys if k.lower() == m.group(0).lower())], r)
            layman_reasons.append(lr)
            
        why_concerned = "\n".join([f"• {r}" for r in layman_reasons])
        actions = ts.get("what_to_do_next") or ts.get("recommended_actions") or []
        
        if risk_level == "Safe":
            not_to_do = ["No further action required."]
        else:
            not_to_do = [
                "Don't send any refund if the sender claims they sent extra money.",
                "Don't trust SMS alerts sent from unknown mobile numbers."
            ]
            
        return generate_whatsapp_response(
            risk_level=risk_level,
            summary=summary,
            what_we_found=what_we_found,
            why_concerned=why_concerned,
            what_to_do=actions if actions else [
                "Open your own banking app.",
                "Check your balance directly to confirm receipt.",
                "Do not release goods until payment reflects."
            ],
            what_not_to_do=not_to_do,
            is_senior=is_senior,
            scam_type="Fake UPI Screenshot"
        )
    
    if risk_level == "Safe":
        return generate_whatsapp_response(
            risk_level="Safe",
            summary="We believe this payment proof is authentic and safe.",
            what_we_found=what_we_found,
            why_concerned="All visual structures and transaction IDs align perfectly with official app templates.",
            what_to_do=[
                "Confirm that the amount is credited to your bank account statement.",
                "Keep this receipt for your records."
            ],
            what_not_to_do=["No further action required."],
            is_senior=is_senior,
            scam_type="Safe Payment Screenshot"
        )

    # Scams
    if is_df:
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This image shows signs of AI manipulation or doctoring.",
            what_we_found={"Subject Name": receiver, "Manipulation Type": deepfake.get("manipulation_type")},
            why_concerned="The facial details and pixels show clear evidence of digital altering.",
            what_to_do=[
                "Do not share this image as it may contain false information.",
                "Ask for a live video call to verify the identity of the person."
            ],
            what_not_to_do=["Don't make payments or trust identity proofs based on visual files alone."],
            is_senior=is_senior,
            scam_type="Deepfake Image"
        )
        
    if any(kw in raw_text for kw in ["court", "notice", "summon", "police", "legal"]):
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This legal notice looks fabricated to induce panic.",
            what_we_found={"Notice Number": tx_id, "Sender": receiver},
            why_concerned="Official notices are never sent informally via WhatsApp, and the document lacks verified government signatures.",
            what_to_do=[
                "Verify the case status on the official e-Courts portal.",
                "Consult a local lawyer or visit the nearest police station."
            ],
            what_not_to_do=[
                "Don't pay any 'settlement fee' demanded over the phone.",
                "Don't share your Aadhaar or PAN card copies."
            ],
            is_senior=is_senior,
            scam_type="Fake Court Notice"
        )
        
    if any(kw in raw_text for kw in ["electricity", "power", "bill", "discom"]):
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This electricity bill notice is a scam.",
            what_we_found={"Consumer Number": upi_id, "Due Amount": amount},
            why_concerned="The payment links lead to a private portal rather than the official power board website.",
            what_to_do=[
                "Pay only through the official electricity board website or app.",
                "Call the customer care number listed on your physical bill."
            ],
            what_not_to_do=[
                "Don't call any phone number provided in this text or notice.",
                "Don't pay under panic or threat of immediate power cut."
            ],
            is_senior=is_senior,
            scam_type="Fake Electricity Bill"
        )
        
    if any(kw in raw_text for kw in ["statement", "ledger", "passbook"]):
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This bank statement appears modified or doctored.",
            what_we_found={"Bank Name": app_name, "Account Number": upi_id, "Amount": amount},
            why_concerned="The font alignments are inconsistent and some transaction entry details seem edited.",
            what_to_do=[
                "Download the statement directly from your official netbanking portal.",
                "Contact your bank branch to verify the transactions."
            ],
            what_not_to_do=[
                "Don't make business decisions based on this document.",
                "Don't share your online banking passwords."
            ],
            is_senior=is_senior,
            scam_type="Fake Bank Statement"
        )
        
    if any(kw in raw_text for kw in ["courier", "parcel", "fedex", "dhl", "delhivery", "customs"]):
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This message is a known courier parcel delivery scam.",
            what_we_found={"Tracking ID": tx_id, "Courier Company": app_name, "Pending Fee": amount},
            why_concerned="It claims a package is blocked due to illegal items and demands online verification fees.",
            what_to_do=[
                "Check the tracking number on the official courier website directly.",
                "Block the sender number immediately."
            ],
            what_not_to_do=[
                "Don't pay any 'customs duty' or 'release charge' online.",
                "Don't download any remote screen-sharing apps."
            ],
            is_senior=is_senior,
            scam_type="Courier Scam"
        )
        
    if any(kw in raw_text for kw in ["invest", "profit", "earn", "trade", "trading", "crypto"]):
        return generate_whatsapp_response(
            risk_level="High Risk",
            summary="This investment scheme is a deceptive scam.",
            what_we_found={"Scheme Name": app_name, "Promised Return": amount},
            why_concerned="The returns promised are unrealistically high and the platform is not registered with regulators.",
            what_to_do=[
                "Always consult a certified financial advisor before investing.",
                "Search for reviews online with the word 'scam' or 'fraud'."
            ],
            what_not_to_do=[
                "Don't join WhatsApp groups promising stock tips or guaranteed profit.",
                "Don't transfer money to personal bank accounts for investing."
            ],
            is_senior=is_senior,
            scam_type="Investment Scam"
        )

    # Default Fake UPI Screenshot
    return generate_whatsapp_response(
        risk_level=risk_level,
        summary="We believe this payment proof is fake and not trustworthy.",
        what_we_found=what_we_found,
        why_concerned="The payment could not be confirmed, and visual templates vary from authentic ones.",
        what_to_do=[
            "Open your own banking app.",
            "Check your balance to see if the money has actually arrived.",
            "Do not hand over goods until the payment reflects in your account."
        ],
        what_not_to_do=[
            "Don't send any refund back if the sender claims they sent extra money.",
            "Don't trust SMS alerts sent from unknown mobile numbers."
        ],
        is_senior=is_senior,
        scam_type="Fake UPI Screenshot"
    )


def format_qr_result(data: dict, is_senior: bool = False) -> str:
    risk = data.get("risk_level", "UNKNOWN")
    payload = data.get("upi_payload") or {}
    
    risk_level = "High Risk" if risk == "HIGH" else "Be Careful" if risk == "MEDIUM" else "Safe"
    
    qr_destination = payload.get("pa") or data.get("raw_qr_data")
    receiver = payload.get("pn")
    amount = payload.get("am")
    
    what_we_found = {
        "QR Destination": qr_destination,
        "Receiver": receiver,
        "Amount": amount
    }

    if risk_level == "Safe":
        return generate_whatsapp_response(
            risk_level="Safe",
            summary="This QR code is safe and points to a valid destination.",
            what_we_found=what_we_found,
            why_concerned="No suspicious redirection patterns or unauthorized merchant links were found.",
            what_to_do=[
                "Make sure you know the receiver before completing the payment.",
                "Double-check the receiver name on the payment screen."
            ],
            what_not_to_do=["No further action required."],
            is_senior=is_senior,
            scam_type="Safe QR Code"
        )

    return generate_whatsapp_response(
        risk_level=risk_level,
        summary="We found this QR code points to a suspicious destination.",
        what_we_found=what_we_found,
        why_concerned="The QR destination address is unverified and could attempt to withdraw money from your account.",
        what_to_do=[
            "Do not scan this QR code using any payment app.",
            "Ask the sender to pay using standard mobile number transfer instead."
        ],
        what_not_to_do=[
            "Don't enter your UPI PIN after scanning any code.",
            "Remember: UPI PIN is only for paying, never for receiving money."
        ],
        is_senior=is_senior,
        scam_type="Fake QR Code"
    )


def format_document_result(data: dict, is_senior: bool = False) -> str:
    risk = data.get("risk_level", "UNKNOWN")
    risk_level = "High Risk" if risk == "HIGH" else "Be Careful" if risk == "MEDIUM" else "Safe"
    explanation = data.get("explanation", "")
    suspicious_urls = data.get("suspicious_urls", [])
    
    urls_str = ", ".join(suspicious_urls) if suspicious_urls else None
    
    what_we_found = {
        "Document Type": data.get("document_type", "PDF"),
        "Page Count": data.get("page_count"),
        "Website": urls_str
    }

    if risk_level == "Safe":
        return generate_whatsapp_response(
            risk_level="Safe",
            summary="This PDF document appears legitimate and safe.",
            what_we_found=what_we_found,
            why_concerned="No malicious scripts, hidden files, or dangerous redirect links were detected.",
            what_to_do=[
                "Open the document safely for your official needs."
            ],
            what_not_to_do=["No further action required."],
            is_senior=is_senior,
            scam_type="Safe Document"
        )

    # Check website scams inside document
    if suspicious_urls:
        return generate_whatsapp_response(
            risk_level=risk_level,
            summary="This document link is unsafe and likely a phishing page.",
            what_we_found=what_we_found,
            why_concerned="The links lead to unverified portals that mimic bank login screens.",
            what_to_do=[
                "Do not click on any link inside this document.",
                "Visit the official netbanking portal manually in your browser."
            ],
            what_not_to_do=[
                "Don't fill any forms or enter passwords on this site.",
                "Don't click any buttons offering cash prizes or lucky draws."
            ],
            is_senior=is_senior,
            scam_type="Suspicious Website"
        )

    return generate_whatsapp_response(
        risk_level=risk_level,
        summary="This PDF document contains malicious elements.",
        what_we_found=what_we_found,
        why_concerned=explanation or "The PDF contains hidden scripts or files that could harm your device.",
        what_to_do=[
            "Delete this PDF file from your phone immediately.",
            "Run a mobile security scan on your phone."
        ],
        what_not_to_do=[
            "Don't open or click on any links inside this document.",
            "Don't share this file with anyone else."
        ],
        is_senior=is_senior,
        scam_type="Malicious PDF"
    )


def format_unified_result(result: dict, is_senior: bool = False) -> str:
    """result is the dict returned by the /scan/unified route."""
    file_type = result.get("file_type")
    try:
        if file_type == "qr":
            return format_qr_result(result.get("qr_result", {}), is_senior)
        if file_type == "pdf":
            return format_document_result(result.get("document_result", {}), is_senior)
        if file_type == "screenshot":
            return format_screenshot_result(result.get("screenshot_result", {}), is_senior)
    except Exception:
        pass
    return (
        "Sorry, I couldn't fully check that file. Please try sending a clear "
        "screenshot, QR code image, or bank statement PDF."
    )
