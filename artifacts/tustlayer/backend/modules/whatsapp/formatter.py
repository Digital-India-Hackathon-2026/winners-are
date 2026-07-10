"""Turns raw scan-pipeline JSON into a short, human WhatsApp message."""


def _risk_emoji(level: str) -> str:
    return {"LOW": "\U0001F7E2", "MEDIUM": "\U0001F7E1", "HIGH": "\U0001F534"}.get(
        (level or "").upper(), "\u26AA"
    )


def format_screenshot_result(data: dict) -> str:
    ts = data.get("trust_score_data", {}) or {}
    ocr = (data.get("ocr_data", {}) or {}).get("extracted_fields", {}) or {}
    score = ts.get("trust_score", 0)
    risk = ts.get("risk_level", "UNKNOWN")
    verdict = ts.get("verdict") or ("Likely Authentic" if score >= 70 else "Suspicious")

    lines = [
        f"*TrustLayer Scan Result* {_risk_emoji(risk)}",
        f"Trust Score: *{score}/100* ({risk})",
        f"Verdict: {verdict}",
        "",
    ]

    amt = ocr.get("payment_amount") or ocr.get("amount")
    utr = ocr.get("upi_transaction_id")
    app = ocr.get("payment_app_name")
    if amt:
        lines.append(f"Amount: {amt}")
    if utr:
        lines.append(f"UTR: {utr}")
    if app:
        lines.append(f"App: {app}")

    reasons = (ts.get("confidence_reasoning") or [])[:3]
    if reasons:
        lines.append("")
        lines.append("*Why:*")
        lines += [f"- {r}" for r in reasons]

    actions = (ts.get("what_to_do_next") or ts.get("recommended_actions") or [])[:3]
    if actions:
        lines.append("")
        lines.append("*Next steps:*")
        lines += [f"- {a}" for a in actions]

    return "\n".join(lines)


def format_qr_result(data: dict) -> str:
    risk = data.get("risk_level", "UNKNOWN")
    payload = data.get("upi_payload") or {}
    lines = [
        f"*QR Code Scan* {_risk_emoji(risk)}",
        f"Risk: {risk}",
    ]
    if not data.get("is_upi_qr"):
        lines.append("This does not look like a valid UPI QR code.")
    else:
        if payload.get("pa"):
            lines.append(f"Pays to (VPA): {payload['pa']}")
        if payload.get("pn"):
            lines.append(f"Name: {payload['pn']}")
        if payload.get("am"):
            lines.append(f"Amount: {payload['am']}")
    signals = (data.get("risk_signals") or [])[:3]
    if signals:
        lines.append("")
        lines.append("*Flags:*")
        lines += [f"- {s}" for s in signals]
    if data.get("explanation"):
        lines.append("")
        lines.append(data["explanation"])
    return "\n".join(lines)


def format_document_result(data: dict) -> str:
    risk = data.get("risk_level", "UNKNOWN")
    lines = [
        f"*Document Scan* {_risk_emoji(risk)}",
        f"Risk: {risk}",
    ]
    if data.get("suspicious_urls"):
        lines.append(f"Suspicious links found: {len(data['suspicious_urls'])}")
    if data.get("steganography_suspected"):
        lines.append("Hidden data patterns detected.")
    signals = (data.get("risk_signals") or [])[:3]
    if signals:
        lines.append("")
        lines.append("*Flags:*")
        lines += [f"- {s}" for s in signals]
    if data.get("explanation"):
        lines.append("")
        lines.append(data["explanation"])
    return "\n".join(lines)


def format_unified_result(result: dict) -> str:
    """result is the dict returned by the /scan/unified route."""
    file_type = result.get("file_type")
    try:
        if file_type == "qr":
            return format_qr_result(result.get("qr_result", {}))
        if file_type == "pdf":
            return format_document_result(result.get("document_result", {}))
        if file_type == "screenshot":
            return format_screenshot_result(result.get("screenshot_result", {}))
    except Exception:
        pass
    return (
        "Sorry, I couldn't fully analyze that file. Please send a clear "
        "screenshot, QR code image, or PDF of the payment proof."
    )
