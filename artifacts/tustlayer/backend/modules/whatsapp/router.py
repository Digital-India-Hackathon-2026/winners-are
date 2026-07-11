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
    import random
    form = dict(await request.form())

    if not await _is_valid_twilio_request(request, form):
        return PlainTextResponse("Invalid signature", status_code=403)

    num_media = int(form.get("NumMedia", "0") or "0")
    inbound_text = form.get("Body", "").strip()
    inbound_text_lower = inbound_text.lower()
    
    is_senior = any(kw in inbound_text_lower for kw in ["senior", "elderly", "grandpa", "grandma", "simple"])
    
    twiml = MessagingResponse()

    # Welcome message if no file is sent
    if num_media == 0:
        if is_senior:
            twiml.message(
                "Hello! I am TrustLayer.\n\n"
                "I am here to help you check if payment pictures or links are safe.\n\n"
                "I am private and safe. I never save your details.\n\n"
                "Please send me any payment picture, QR code, website, or document.\n\n"
                "I will read it and guide you step by step."
            )
        else:
            twiml.message(
                "Hello! I am TrustLayer, your digital safety assistant. I help you verify if a payment screenshot, QR code, website link, or document is safe to trust.\n\n"
                "Your files are checked securely and privately. They are never saved or shared with anyone.\n\n"
                "Just send me any suspicious screenshot, QR code, website link, or PDF. I'll inspect it carefully and let you know if it's safe."
            )
        return Response(content=str(twiml), media_type="application/xml")

    # Rotated reassuring acknowledgments
    ack_options = [
        "I've received your file and I'm checking it carefully. This usually takes less than 15 seconds.",
        "File uploaded successfully! I am examining it for security details now. Back in a few seconds.",
        "Got your document. Analyzing the details and checking safety records...",
        "Perfect, I've got the file. Let me run a security check on this for you."
    ]
    ack_msg = random.choice(ack_options)
    
    if is_senior:
        ack_msg = "I have received your file. Please wait a moment while I check it carefully for you. This will take less than 15 seconds."
        
    twiml.message(ack_msg)

    media_url = form.get("MediaUrl0")
    content_type = form.get("MediaContentType0", "")

    try:
        file_bytes = await download_twilio_media(media_url)
        reply_text = await analyze_media(file_bytes, content_type, is_senior)
    except Exception as e:
        print(f"[WhatsApp] Webhook error: {e}")
        if is_senior:
            reply_text = "I am sorry, I could not read that file. Please try sending it again clearly."
        else:
            reply_text = (
                "Sorry, I couldn't download or read that file. Please try "
                "resending it."
            )

    twiml.message(reply_text)
    return Response(content=str(twiml), media_type="application/xml")
