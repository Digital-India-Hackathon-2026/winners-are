"""
TrustLayer AI – QR Inspector Service v2.0
"""
from backend.modules.qr_inspector.schemas import QRInspectionResult, UPIQRPayload
from backend.modules.qr_inspector.engine import QRInspectorEngine


class QRInspectorService:
    def __init__(self):
        self.engine = QRInspectorEngine()

    async def inspect(self, image_bytes: bytes) -> QRInspectionResult:
        try:
            qr_texts, qr_count = self.engine.extract_qr_codes(image_bytes)

            if not qr_texts:
                return QRInspectionResult(
                    success=True,
                    qr_found=False,
                    qr_count=0,
                    explanation="No QR code found in image.",
                )

            # Analyze the first (primary) QR
            analysis = self.engine.analyze_qr_data(qr_texts[0])
            all_signals = list(analysis["risk_signals"])

            multiple_qr = qr_count > 1
            if multiple_qr:
                all_signals.append(f"Multiple QR codes detected ({qr_count}) — only first analyzed")

            # Build UPI payload if present
            upi_payload = None
            if analysis["payload"]:
                p = analysis["payload"]
                upi_payload = UPIQRPayload(
                    raw_uri=p["raw_uri"],
                    pa=p.get("pa"),
                    pn=p.get("pn"),
                    am=p.get("am"),
                    tn=p.get("tn"),
                    tr=p.get("tr"),
                    mc=p.get("mc"),
                    cu=p.get("cu"),
                    mode=p.get("mode"),
                    sign=p.get("sign"),
                )

            # Determine risk level
            critical_flags = analysis["foreign_currency"] or (analysis["unknown_vpa"] and not analysis["is_upi"])
            medium_flags = analysis["amount_hardcoded"] or analysis["suspicious_uri"] or analysis["unknown_vpa"]

            if critical_flags or multiple_qr:
                risk_level = "HIGH"
            elif medium_flags:
                risk_level = "MEDIUM"
            elif analysis["is_upi"]:
                risk_level = "LOW"
            else:
                risk_level = "MEDIUM"

            explanation = (
                f"Found {qr_count} QR code(s). "
                + ("UPI QR detected. " if analysis["is_upi"] else "Non-UPI QR code. ")
                + (f"Risk: {risk_level}.")
            )

            return QRInspectionResult(
                success=True,
                qr_found=True,
                qr_count=qr_count,
                is_upi_qr=analysis["is_upi"],
                upi_payload=upi_payload,
                foreign_currency=analysis["foreign_currency"],
                amount_hardcoded=analysis["amount_hardcoded"],
                unknown_vpa_handle=analysis["unknown_vpa"],
                vpa_handle_valid=analysis["vpa_handle_valid"],
                multiple_qr_codes=multiple_qr,
                suspicious_uri=analysis["suspicious_uri"],
                risk_level=risk_level,
                risk_signals=all_signals,
                explanation=explanation,
            )

        except Exception as e:
            print(f"[QR-INSPECTOR] Service error: {e}")
            return QRInspectionResult(
                success=False,
                error=str(e),
                explanation="QR inspection failed due to an internal error.",
            )


def get_qr_inspector_service() -> QRInspectorService:
    return QRInspectorService()
