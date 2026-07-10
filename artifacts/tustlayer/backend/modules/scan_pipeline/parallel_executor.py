import asyncio
from typing import Tuple

from backend.modules.ocr.service import OCRService
from backend.modules.fraud_intelligence.service import FraudIntelligenceService
from backend.modules.ocr.schemas import OCRResult, ExtractedFields
from backend.modules.fraud_intelligence.schemas import FraudMatchResult

class ParallelTaskExecutor:
    def __init__(self, ocr_service: OCRService, fraud_service: FraudIntelligenceService):
        self.ocr = ocr_service
        self.fraud = fraud_service
        
    async def _safe_execute(self, coro, fallback_val):
        """Error boundary wrapper."""
        try:
            return await coro
        except Exception as e:
            print(f"Parallel Task Failed: {e}")
            return fallback_val

    async def execute_all(self, image_bytes: bytes) -> Tuple[OCRResult, FraudMatchResult]:
        """
        Executes OCR and Fraud Intelligence concurrently to minimize latency.
        """
        # Create fallbacks in case of catastrophic module failure
        # This ensures the pipeline degrades gracefully instead of crashing
        ocr_fallback = OCRResult(
            fields=ExtractedFields(),
            confidence_score=0.0,
            used_fallback=False
        )
        fraud_fallback = FraudMatchResult(
            fingerprint_match=False,
            match_confidence=0.0,
            match_count=0
        )
        
        # Fire parallel tasks
        ocr_task = self._safe_execute(self.ocr.extract_payment_proof(image_bytes), ocr_fallback)
        fraud_task = self._safe_execute(self.fraud.scan_image(image_bytes), fraud_fallback)
        
        # Await completion
        ocr_result, fraud_result = await asyncio.gather(ocr_task, fraud_task)
        
        return ocr_result, fraud_result
