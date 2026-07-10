"""
TrustLayer AI – Document Scanner Service v2.0
"""
from backend.modules.document_scanner.schemas import DocumentThreatResult
from backend.modules.document_scanner.engine import DocumentScannerEngine


class DocumentScannerService:
    def __init__(self):
        self.engine = DocumentScannerEngine()

    async def scan(self, file_bytes: bytes, content_type: str) -> DocumentThreatResult:
        try:
            is_pdf = "pdf" in content_type.lower() or file_bytes[:4] == b"%PDF"

            # Render PDF pages to images and run safety/nsfw classification
            if is_pdf:
                try:
                    import fitz
                    from backend.integrations.groq_client import GroqVisionProvider
                    doc = fitz.open(stream=file_bytes, filetype="pdf")
                    num_pages = len(doc)
                    
                    groq_vision = GroqVisionProvider()
                    max_moderate_pages = min(num_pages, 5)
                    for page_num in range(max_moderate_pages):
                        page = doc.load_page(page_num)
                        pix = page.get_pixmap(dpi=150)
                        img_data = pix.tobytes("png")
                        
                        safety_res = await groq_vision.verify_page_safety(img_data)
                        if not safety_res.get("is_safe", True):
                            print(f"[DOC-SAFETY] Flagged NSFW content on page {page_num + 1}!")
                            category = safety_res.get("flagged_category", "NSFW")
                            explanation = f"Blocked: Content Policy Violation. Flagged category: '{category}' detected on Page {page_num + 1}."
                            return DocumentThreatResult(
                                success=False,
                                document_type="pdf",
                                page_count=num_pages,
                                steganography_suspected=False,
                                steganography_signals=[],
                                urls_found=[],
                                suspicious_urls=[],
                                url_risk_level="HIGH",
                                url_analysis=[],
                                embedded_files_found=False,
                                embedded_file_count=0,
                                pdf_javascript_found=False,
                                pdf_auto_action_found=False,
                                risk_level="HIGH",
                                risk_signals=[f"NSFW content violation on Page {page_num + 1}"],
                                explanation=explanation,
                            )
                except Exception as safety_err:
                    print(f"[DOC-SAFETY] Page moderation failed/skipped: {safety_err}")

            if is_pdf:
                raw = self.engine.analyze_pdf(file_bytes)
            else:
                raw = self.engine.analyze_image(file_bytes)

            risk_signals = list(raw.get("steganography_signals", []))

            # Per-URL analysis with reasons
            url_analysis = raw.get("url_analysis", [])
            if raw.get("suspicious_urls"):
                for analysis in url_analysis:
                    if analysis.get("risk") in ("HIGH", "MEDIUM"):
                        url_str = analysis["url"][:80]
                        reasons_str = "; ".join(analysis.get("reasons", []))
                        risk_signals.append(f"⚠ {url_str} — {reasons_str}")

            if raw.get("pdf_javascript_found"):
                risk_signals.append("JavaScript found in PDF")
            if raw.get("pdf_auto_action_found"):
                risk_signals.append("Auto-action trigger found in PDF")
            if raw.get("embedded_files_found"):
                risk_signals.append(f"{raw['embedded_file_count']} embedded file(s) in PDF")

            # Determine risk level — use url_analysis for more granular detection
            has_high_risk_urls = any(a.get("risk") == "HIGH" for a in url_analysis)
            has_medium_risk_urls = any(a.get("risk") == "MEDIUM" for a in url_analysis)

            critical = (
                raw.get("steganography_suspected")
                or raw.get("pdf_javascript_found")
                or raw.get("pdf_auto_action_found")
                or (has_high_risk_urls and len(raw.get("suspicious_urls", [])) >= 2)
            )
            medium = (
                has_high_risk_urls
                or has_medium_risk_urls
                or raw.get("embedded_files_found")
            )

            if critical:
                risk_level = "HIGH"
            elif medium:
                risk_level = "MEDIUM"
            else:
                risk_level = "LOW"

            # URL risk level: HIGH if any HIGH-risk URL, MEDIUM if any MEDIUM
            if has_high_risk_urls:
                url_risk = "HIGH"
            elif has_medium_risk_urls:
                url_risk = "MEDIUM"
            elif url_analysis:
                url_risk = "LOW"
            else:
                url_risk = "NONE"

            doc_type = raw.get("document_type", "unknown")
            pages = raw.get("page_count", 0)
            explanation = (
                f"Scanned {doc_type.upper()}"
                + (f" ({pages} pages)" if pages > 0 else "")
                + f". Risk level: {risk_level}."
                + (f" {len(risk_signals)} signal(s) detected." if risk_signals else " No threats found.")
            )

            return DocumentThreatResult(
                success=True,
                document_type=doc_type,
                page_count=pages,
                steganography_suspected=raw.get("steganography_suspected", False),
                steganography_signals=raw.get("steganography_signals", []),
                urls_found=raw.get("urls_found", []),
                suspicious_urls=raw.get("suspicious_urls", []),
                url_risk_level=url_risk,
                url_analysis=url_analysis,
                embedded_files_found=raw.get("embedded_files_found", False),
                embedded_file_count=raw.get("embedded_file_count", 0),
                pdf_javascript_found=raw.get("pdf_javascript_found", False),
                pdf_auto_action_found=raw.get("pdf_auto_action_found", False),
                risk_level=risk_level,
                risk_signals=risk_signals,
                explanation=explanation,
            )

        except Exception as e:
            print(f"[DOC-SCANNER] Service error: {e}")
            return DocumentThreatResult(
                success=False,
                error=str(e),
                explanation="Document scan failed due to an internal error.",
            )


def get_document_scanner_service() -> DocumentScannerService:
    return DocumentScannerService()
