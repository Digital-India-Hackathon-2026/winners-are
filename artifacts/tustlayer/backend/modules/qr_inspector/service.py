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

            # Perform surrounding OCR for cross-validation if a QR is found
            ocr_res = None
            try:
                from backend.modules.ocr.service import get_ocr_service
                ocr_serv = get_ocr_service()
                ocr_res = await ocr_serv.extract_payment_proof(image_bytes)
                print(f"[QR-SERVICE] Successfully extracted surrounding OCR for cross-validation.")
            except Exception as ocr_err:
                print(f"[QR-SERVICE] Surrounding OCR extraction failed: {ocr_err}")

            # Analyze the first (primary) QR using the multi-layer engine
            analysis = await self.engine.analyze_qr_data(qr_texts[0], image_bytes=image_bytes, ocr_result=ocr_res)
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

            # Determine risk level from deterministic engine score
            engine_score = analysis.get("score", 100.0)
            if engine_score >= 80:
                risk_level = "LOW"
            elif engine_score >= 40:
                risk_level = "MEDIUM"
            else:
                risk_level = "HIGH"

            # Override/adjust if critical flags are present
            if multiple_qr:
                risk_level = "HIGH"

            explanation = (
                f"Found {qr_count} QR code(s). Type: {analysis['qr_type']}. "
                f"Verdict: {analysis['verdict']} (Score: {engine_score:.0f}/100). Risk: {risk_level}."
            )

            return QRInspectionResult(
                success=True,
                qr_found=True,
                qr_count=qr_count,
                is_upi_qr=analysis["is_upi"],
                is_upi=analysis["is_upi"],
                raw_qr_data=qr_texts[0],
                upi_payload=upi_payload,
                foreign_currency=analysis["foreign_currency"],
                amount_hardcoded=analysis["amount_hardcoded"],
                unknown_vpa_handle=analysis["unknown_vpa"],
                vpa_handle_valid=analysis["vpa_handle_valid"],
                multiple_qr_codes=multiple_qr,
                suspicious_uri=analysis["suspicious_uri"],
                risk_level=risk_level,
                risk_signals=all_signals,
                resolved_url=analysis.get("resolved_url"),
                explanation=explanation,
                
                # New v2.2 Engine fields
                qr_type=analysis["qr_type"],
                qr_format_valid=analysis["qr_format_valid"],
                missing_mandatory_params=analysis["missing_mandatory_params"],
                duplicate_params=analysis["duplicate_params"],
                ocr_cross_matched=analysis["ocr_cross_matched"],
                ocr_mismatches=analysis["ocr_mismatches"],
                safe_browsing_threat=analysis["safe_browsing_threat"],
                domain_reputation_score=analysis["domain_reputation_score"],
                image_authenticity_issues=analysis["image_authenticity_issues"],
                verdict=analysis["verdict"],
                guidance=analysis["guidance"],
                hash_sha256=analysis["hash_sha256"]
            )

        except Exception as e:
            print(f"[QR-INSPECTOR] Service error: {e}")
            import traceback
            traceback.print_exc()
            return QRInspectionResult(
                success=False,
                error=str(e),
                explanation="QR inspection failed due to an internal error.",
            )


def get_qr_inspector_service() -> QRInspectorService:
    return QRInspectorService()
