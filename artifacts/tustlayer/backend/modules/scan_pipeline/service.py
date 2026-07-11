"""
TrustLayer AI – Scan Pipeline Service v2.0
9-layer forensic pipeline per PRD v2.0.

Layer execution order:
  1+2. OCR + Fraud pHash (parallel)
  3.   App Forensics (color fingerprint, 15 apps)
  4.   EXIF / Metadata (enhanced v2)
  5.   Deepfake Detection (Hive via NVIDIA NIM)
  6.   VPA Validation (Razorpay live lookup)
  7.   Aggregation → TrustScoreInput v2
  8.   Trust Score Engine v2 (additive + hard caps)
  9.   AI Reasoning (Qwen 397B → Phi fallback) + What To Do Next
"""
import time
import json
import asyncio
from typing import Optional
from fastapi import HTTPException

from backend.modules.scan_pipeline.schemas import (
    FinalScanResponse, ScanMetadata,
    DeepfakeScanResult, VPAValidationResult, DeterministicFlags,
)
from backend.modules.scan_pipeline.parallel_executor import ParallelTaskExecutor
from backend.modules.scan_pipeline.aggregator import ResultAggregator
from backend.modules.scan_pipeline.metadata import MetadataService
from backend.integrations.supabase_client import save_scan_result_async

from backend.modules.ocr.service import get_ocr_service
from backend.modules.fraud_intelligence.service import get_fraud_intelligence_service
from backend.modules.trust_score.service import get_final_decision_assembler
from backend.modules.app_forensics.service import get_app_forensics_service
from backend.modules.deepfake.service import get_deepfake_service
from backend.modules.vpa_validator.service import get_vpa_validator_service


class ScanPipelineService:
    def __init__(self):
        self.executor = ParallelTaskExecutor(
            ocr_service=get_ocr_service(),
            fraud_service=get_fraud_intelligence_service()
        )
        self.app_forensics_service = get_app_forensics_service()
        self.aggregator = ResultAggregator()
        self.trust_engine = get_final_decision_assembler()
        self.metadata_service = MetadataService()
        self.deepfake_service = get_deepfake_service()
        self.vpa_service = get_vpa_validator_service()

    async def execute_full_scan(self, image_bytes: bytes) -> FinalScanResponse:
        start_time = time.time()

        # ── Layers 1+2: OCR + Fraud pHash (parallel) ─────────────────────────
        ocr_result, fraud_result = await self.executor.execute_all(image_bytes)

        # ── Non-receipt guard (Step 7) ────────────────────────────────────────
        _extractable = [
            ocr_result.fields.payment_amount, ocr_result.fields.receiver_name,
            ocr_result.fields.upi_id, ocr_result.fields.transaction_reference,
            ocr_result.fields.payment_app, ocr_result.fields.timestamp,
            ocr_result.fields.payment_status if ocr_result.fields.payment_status != "UNKNOWN" else None,
        ]
        _extracted = sum(1 for f in _extractable if f)
        _status = (ocr_result.fields.payment_status or "").upper()
        if _extracted < 2 and _status not in {"SUCCESS", "FAILED", "PENDING"}:
            print(f"[PIPELINE] Non-receipt rejected: extracted={_extracted}, status={_status}")
            raise HTTPException(
                status_code=422,
                detail="This doesn't look like a completed UPI payment receipt. "
                       "Please send a screenshot of a successful payment confirmation."
            )

        # ── Layer 3: App Forensics ────────────────────────────────────────────
        app_forensics_result = await self.app_forensics_service.analyze_image(
            image_bytes, ocr_result.raw_text or "", ocr_result.fields.payment_app
        )

        # ── Layer 4: Enhanced EXIF/Metadata ──────────────────────────────────
        exif_result = self.metadata_service.analyze(image_bytes)

        # ── Layers 5+6: Deepfake + VPA (parallel) ─────────────────────────────
        upi_id = ocr_result.fields.upi_id

        async def _noop():
            return None

        deepfake_raw, vpa_raw = await asyncio.gather(
            self.deepfake_service.analyze(image_bytes),
            self.vpa_service.validate(upi_id, ocr_result.fields.receiver_name) if upi_id else _noop(),
            return_exceptions=True
        )

        # Handle exceptions gracefully
        if isinstance(deepfake_raw, Exception):
            print(f"[PIPELINE] Deepfake layer failed: {deepfake_raw}")
            deepfake_raw = None
        if isinstance(vpa_raw, Exception) or vpa_raw is None:
            vpa_raw = None

        deepfake_score = deepfake_raw.deepfake_probability if deepfake_raw else 0.0
        vpa_exists = vpa_raw.vpa_exists if vpa_raw else None
        vpa_name_match = vpa_raw.name_match if vpa_raw else None

        # ── Layer 7: Aggregation ──────────────────────────────────────────────
        trust_input = self.aggregator.normalize_to_trust_input(
            ocr=ocr_result,
            fraud=fraud_result,
            metadata_anomalies=exif_result.anomaly_count,
            app_forensics=app_forensics_result,
            exif_result=exif_result,
            deepfake_score=deepfake_score,
            vpa_exists_razorpay=vpa_exists,
            vpa_name_match=vpa_name_match,
        )

        # ── Layers 8+9: Trust Score + AI Reasoning ───────────────────────────
        trust_result = await self.trust_engine.evaluate(trust_input)

        # ── Assemble response ─────────────────────────────────────────────────
        execution_ms = int((time.time() - start_time) * 1000)
        modules_run = ["OCR", "FraudIntelligence", "AppForensics", "Metadata", "Deepfake", "VPAValidator", "TrustScore", "AIReasoning"]

        # Build structured sub-objects for new v2 fields
        deepfake_data = None
        if deepfake_raw:
            deepfake_data = DeepfakeScanResult(
                deepfake_probability=deepfake_raw.deepfake_probability,
                is_deepfake=deepfake_raw.is_deepfake,
                manipulation_type=deepfake_raw.manipulation_type,
                signals=deepfake_raw.signals,
                error=deepfake_raw.error,
            )

        vpa_data = None
        if vpa_raw:
            vpa_data = VPAValidationResult(
                upi_id=upi_id,
                vpa_handle_valid=trust_input.vpa_handle_valid,
                vpa_exists=vpa_raw.vpa_exists,
                registered_name=vpa_raw.registered_name,
                name_match=vpa_raw.name_match,
                error=vpa_raw.error,
            )

        det_flags = DeterministicFlags(
            foreign_currency_detected=trust_input.foreign_currency_detected,
            utr_format_violation=trust_input.utr_format_violation,
            utr_dummy_pattern=trust_input.utr_dummy_pattern,
            exif_editing_software=trust_input.exif_editing_software,
            exif_software_name=trust_input.exif_software_name,
            timestamp_late_night=trust_input.timestamp_late_night,
            replay_detected=trust_input.replay_detected,
            replay_count=trust_input.replay_count,
            score_breakdown=trust_result.score_breakdown,
        )

        final_response = FinalScanResponse(
            success=True,
            metadata=ScanMetadata(
                execution_time_ms=execution_ms,
                modules_executed=modules_run,
            ),
            trust_score_data=trust_result,
            ocr_data=ocr_result,
            fraud_intelligence_data=fraud_result,
            app_forensics=app_forensics_result,
            deepfake_data=deepfake_data,
            vpa_validation_data=vpa_data,
            deterministic_flags=det_flags,
        )

        asyncio.create_task(save_scan_result_async(final_response.model_dump()))
        return final_response

    async def stream_full_scan(
        self,
        image_bytes: bytes,
        session_id: Optional[str] = None,
        remaining_scans: int = -1
    ):
        """Generator for Server-Sent Events (SSE) — 9-layer v2 pipeline."""
        start_time = time.time()

        yield f'data: {json.dumps({"status": "processing", "step": "starting", "message": "Initializing TrustLayer v2 Pipeline..."})}\n\n'
        await asyncio.sleep(0.3)

        # Layers 1+2
        yield f'data: {json.dumps({"status": "processing", "step": "scanning", "message": "Running OCR and Fraud Intelligence concurrently..."})}\n\n'
        ocr_result, fraud_result = await self.executor.execute_all(image_bytes)
        exif_result = self.metadata_service.analyze(image_bytes)

        # Non-receipt guard (Step 7)
        _extractable = [
            ocr_result.fields.payment_amount, ocr_result.fields.receiver_name,
            ocr_result.fields.upi_id, ocr_result.fields.transaction_reference,
            ocr_result.fields.payment_app, ocr_result.fields.timestamp,
            ocr_result.fields.payment_status if ocr_result.fields.payment_status != "UNKNOWN" else None,
        ]
        _extracted = sum(1 for f in _extractable if f)
        _status = (ocr_result.fields.payment_status or "").upper()
        if _extracted < 2 and _status not in {"SUCCESS", "FAILED", "PENDING"}:
            print(f"[PIPELINE] Non-receipt rejected (stream): extracted={_extracted}, status={_status}")
            _msg = "This doesn't look like a completed UPI payment receipt. Please send a screenshot of a successful payment confirmation."
            yield f'data: {json.dumps({"status": "error", "step": "rejected", "message": _msg})}\n\n'
            return

        # Layer 3
        yield f'data: {json.dumps({"status": "processing", "step": "app_detection", "message": "Verifying app branding and color fingerprints..."})}\n\n'
        app_forensics_result = await self.app_forensics_service.analyze_image(
            image_bytes, ocr_result.raw_text or "", ocr_result.fields.payment_app
        )

        # Layers 5+6 in parallel
        yield f'data: {json.dumps({"status": "processing", "step": "ai_layers", "message": "Running Deepfake Detection and VPA Validation..."})}\n\n'
        upi_id = ocr_result.fields.upi_id

        deepfake_raw, vpa_raw = await asyncio.gather(
            self.deepfake_service.analyze(image_bytes),
            self.vpa_service.validate(upi_id, ocr_result.fields.receiver_name) if upi_id else asyncio.sleep(0),
            return_exceptions=True
        )

        if isinstance(deepfake_raw, Exception):
            deepfake_raw = None
        if isinstance(vpa_raw, Exception) or vpa_raw is None:
            vpa_raw = None

        deepfake_score = deepfake_raw.deepfake_probability if deepfake_raw else 0.0
        vpa_exists = vpa_raw.vpa_exists if vpa_raw else None
        vpa_name_match = vpa_raw.name_match if vpa_raw else None

        # Layer 7 + 8 + 9
        yield f'data: {json.dumps({"status": "processing", "step": "scoring", "message": "Computing Trust Score and AI Forensic Reasoning..."})}\n\n'

        trust_input = self.aggregator.normalize_to_trust_input(
            ocr=ocr_result,
            fraud=fraud_result,
            metadata_anomalies=exif_result.anomaly_count,
            app_forensics=app_forensics_result,
            exif_result=exif_result,
            deepfake_score=deepfake_score,
            vpa_exists_razorpay=vpa_exists,
            vpa_name_match=vpa_name_match,
        )
        trust_result = await self.trust_engine.evaluate(trust_input)

        execution_ms = int((time.time() - start_time) * 1000)
        modules_run = ["OCR", "FraudIntelligence", "AppForensics", "Metadata", "Deepfake", "VPAValidator", "TrustScore", "AIReasoning"]

        deepfake_data = None
        if deepfake_raw:
            deepfake_data = DeepfakeScanResult(
                deepfake_probability=deepfake_raw.deepfake_probability,
                is_deepfake=deepfake_raw.is_deepfake,
                manipulation_type=deepfake_raw.manipulation_type,
                signals=deepfake_raw.signals,
            )

        vpa_data = None
        if vpa_raw:
            vpa_data = VPAValidationResult(
                upi_id=upi_id,
                vpa_handle_valid=trust_input.vpa_handle_valid,
                vpa_exists=vpa_raw.vpa_exists,
                registered_name=vpa_raw.registered_name,
                name_match=vpa_raw.name_match,
                error=vpa_raw.error,
            )

        det_flags = DeterministicFlags(
            foreign_currency_detected=trust_input.foreign_currency_detected,
            utr_format_violation=trust_input.utr_format_violation,
            utr_dummy_pattern=trust_input.utr_dummy_pattern,
            exif_editing_software=trust_input.exif_editing_software,
            exif_software_name=trust_input.exif_software_name,
            timestamp_late_night=trust_input.timestamp_late_night,
            replay_detected=trust_input.replay_detected,
            replay_count=trust_input.replay_count,
            score_breakdown=trust_result.score_breakdown,
        )

        final_response = FinalScanResponse(
            success=True,
            metadata=ScanMetadata(
                execution_time_ms=execution_ms,
                modules_executed=modules_run,
            ),
            trust_score_data=trust_result,
            ocr_data=ocr_result,
            fraud_intelligence_data=fraud_result,
            app_forensics=app_forensics_result,
            deepfake_data=deepfake_data,
            vpa_validation_data=vpa_data,
            deterministic_flags=det_flags,
            anonymous_session_id=session_id,
            remaining_scans=remaining_scans,
        )

        yield f'data: {json.dumps({"status": "complete", "step": "finalized", "payload": final_response.model_dump()})}\n\n'
        asyncio.create_task(save_scan_result_async(final_response.model_dump()))


def get_scan_pipeline_service() -> ScanPipelineService:
    return ScanPipelineService()
