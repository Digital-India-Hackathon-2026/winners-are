from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator

from backend.core.config import settings
from backend.modules.whatsapp.service import download_twilio_media, analyze_media

router = APIRouter(prefix="/api/v1/whatsapp", tags=["WhatsApp Bot"])


async def _is_valid_twilio_request(request: Request, form: dict) -> bool:
    """Verifies the X-Twilio-Signature header so random callers can't hit the
    webhook. Skipped automatically if TWILIO_AUTH_TOKEN isn't configured yet
    (e.g. local dev), so setup can proceed incrementally."""
    if not settings.TWILIO_AUTH_TOKEN:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    url = str(request.url)
    return validator.validate(url, form, signature)


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
    """Twilio WhatsApp inbound webhook. Configure this URL (e.g.
    https://your-domain.com/api/v1/whatsapp/webhook) as the 'WHEN A MESSAGE
    COMES IN' webhook for your Twilio WhatsApp sender."""
    form = dict(await request.form())

    if not await _is_valid_twilio_request(request, form):
        return PlainTextResponse("Invalid signature", status_code=403)

    num_media = int(form.get("NumMedia", "0") or "0")
    twiml = MessagingResponse()

    if num_media == 0:
        twiml.message(
            "Send me a screenshot of a UPI payment, a QR code image, or a "
            "payment PDF and I'll check it for signs of fraud."
        )
        return Response(content=str(twiml), media_type="application/xml")

    media_url = form.get("MediaUrl0")
    content_type = form.get("MediaContentType0", "")

    try:
        file_bytes = await download_twilio_media(media_url)
        reply_text = await analyze_media(file_bytes, content_type)
    except Exception as e:
        print(f"[WhatsApp] Webhook error: {e}")
        reply_text = (
            "Sorry, I couldn't download or read that file. Please try "
            "resending it."
        )

    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")
