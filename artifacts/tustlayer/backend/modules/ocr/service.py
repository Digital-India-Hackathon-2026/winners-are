"""
TrustLayer AI – OCR Service v2.1
Thin wrapper around NvidiaFirstOCREngine. AI-first pipeline.
"""
from backend.modules.ocr.schemas import OCRResult
from backend.modules.ocr.engine import NvidiaFirstOCREngine


class OCRService:
    """Thin service wrapper around NvidiaFirstOCREngine."""

    def __init__(self):
        self.engine = NvidiaFirstOCREngine()

    async def extract_payment_proof(self, image_bytes: bytes) -> OCRResult:
        """Extract payment fields from screenshot. AI-first pipeline."""
        return await self.engine.extract(image_bytes)


def get_ocr_service() -> OCRService:
    return OCRService()
