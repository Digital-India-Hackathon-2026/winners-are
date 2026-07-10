import httpx
from backend.core.config import settings
from backend.modules.scan_pipeline.service import get_scan_pipeline_service
from backend.modules.qr_inspector.service import get_qr_inspector_service
from backend.modules.document_scanner.service import get_document_scanner_service
from backend.modules.whatsapp.formatter import (
    format_screenshot_result,
    format_qr_result,
    format_document_result,
)

MAX_MEDIA_BYTES = 15 * 1024 * 1024  # WhatsApp media cap


async def download_twilio_media(media_url: str) -> bytes:
    """Twilio media URLs require HTTP Basic Auth if secure media is enabled, or can be fetched publicly."""
    async with httpx.AsyncClient(timeout=20.0) as client:
        # If Twilio keys are configured, use basic auth; otherwise fetch publicly
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            try:
                resp = await client.get(media_url, auth=auth, follow_redirects=True)
                if resp.status_code == 200:
                    return resp.content
            except Exception as e:
                print(f"[WhatsApp] Auth media download failed, trying public fallback: {e}")
        
        # Fallback public download (Sandbox/standard accounts default)
        resp = await client.get(media_url, follow_redirects=True)
        resp.raise_for_status()
        return resp.content


async def analyze_media(file_bytes: bytes, content_type: str) -> str:
    """Routes bytes through the same detection pipeline used by the web app,
    then returns a short, WhatsApp-ready summary string."""
    if len(file_bytes) > MAX_MEDIA_BYTES:
        return "That file is too large to analyze. Please send a file under 15MB."

    is_pdf = "pdf" in (content_type or "").lower() or file_bytes[:4] == b"%PDF"

    try:
        if is_pdf:
            doc_service = get_document_scanner_service()
            res = await doc_service.scan(file_bytes, content_type)
            return format_document_result(res.model_dump())

        qr_service = get_qr_inspector_service()
        qr_res = await qr_service.inspect(file_bytes)
        if qr_res.qr_found:
            return format_qr_result(qr_res.model_dump())

        scan_service = get_scan_pipeline_service()
        scan_res = await scan_service.execute_full_scan(file_bytes)
        return format_screenshot_result(scan_res.model_dump())
    except Exception as e:
        print(f"[WhatsApp] Analysis failed: {e}")
        return (
            "Sorry, something went wrong while analyzing that file. "
            "Please try sending a clearer image or PDF."
        )
