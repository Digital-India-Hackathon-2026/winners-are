from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Response
from fastapi.responses import StreamingResponse
from backend.modules.scan_pipeline.schemas import FinalScanResponse
from backend.modules.scan_pipeline.service import ScanPipelineService, get_scan_pipeline_service
from backend.modules.scan_pipeline.middleware import get_session_or_user

router = APIRouter(prefix="/api/v1/scan", tags=["Scan Pipeline"])

@router.post("/execute", response_model=FinalScanResponse)
async def execute_scan(
    response: Response,
    file: UploadFile = File(...),
    service: ScanPipelineService = Depends(get_scan_pipeline_service),
    context: dict = Depends(get_session_or_user)
):
    """
    MASTER ENDPOINT: Accepts an image upload, runs OCR and Fraud Intelligence concurrently,
    aggregates the results, and returns the cinematic final Trust Score payload.
    Enforces auth-optional guest sessions and limits.
    """
    try:
        image_bytes = await file.read()
        scan_response = await service.execute_full_scan(image_bytes)
        
        # Populate session metadata
        if not context.get("is_authenticated"):
            scan_response.anonymous_session_id = context.get("uid")
        scan_response.remaining_scans = context.get("remaining_scans", -1)
        
        # Expose response headers
        response.headers["X-Anonymous-Session-ID"] = context.get("uid")
        response.headers["X-Remaining-Scans"] = str(context.get("remaining_scans", -1))
        
        return scan_response
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Master Scan Pipeline Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to execute full scan pipeline."
        )

@router.post("/stream")
async def stream_scan(
    response: Response,
    file: UploadFile = File(...),
    service: ScanPipelineService = Depends(get_scan_pipeline_service),
    context: dict = Depends(get_session_or_user)
):
    """
    SERVER-SENT EVENTS ENDPOINT: Streams the pipeline progress back to the client
    for progressive UI loading animations.
    """
    try:
        image_bytes = await file.read()
        
        # Expose response headers
        response.headers["X-Anonymous-Session-ID"] = context.get("uid")
        response.headers["X-Remaining-Scans"] = str(context.get("remaining_scans", -1))
        
        return StreamingResponse(
            service.stream_full_scan(
                image_bytes,
                session_id=None if context.get("is_authenticated") else context.get("uid"),
                remaining_scans=context.get("remaining_scans", -1)
            ),
            media_type="text/event-stream"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Streaming Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start streaming pipeline."
        )


@router.post("/unified")
async def execute_unified_scan(
    response: Response,
    file: UploadFile = File(...),
    service: ScanPipelineService = Depends(get_scan_pipeline_service),
    context: dict = Depends(get_session_or_user)
):
    """
    Unified entrypoint for all verification methods (image, PDF, QR).
    Detects the file type and routes it dynamically to DocumentScannerService,
    QRInspectorService, or the standard transaction image verification pipeline.
    """
    try:
        filename = file.filename or ""
        content_type = file.content_type or ""
        
        # Read a small chunk to check PDF magic bytes safely
        header_chunk = await file.read(4)
        is_pdf = "pdf" in content_type.lower() or filename.lower().endswith(".pdf") or header_chunk == b"%PDF"
        
        # Reset pointer for full read
        await file.seek(0)
        file_bytes = await file.read()
        
        # 1. PDF Document routing
        if is_pdf:
            from backend.modules.document_scanner.service import get_document_scanner_service
            doc_service = get_document_scanner_service()
            res = await doc_service.scan(file_bytes, content_type)
            return {
                "file_type": "pdf",
                "document_result": res.model_dump(),
                "anonymous_session_id": context.get("uid"),
                "remaining_scans": context.get("remaining_scans", -1)
            }
            
        # 2. Image routing: Check for QR codes first
        from backend.modules.qr_inspector.service import get_qr_inspector_service
        qr_service = get_qr_inspector_service()
        qr_res = await qr_service.inspect(file_bytes)
        
        if qr_res.qr_found:
            return {
                "file_type": "qr",
                "qr_result": qr_res.model_dump(),
                "anonymous_session_id": context.get("uid"),
                "remaining_scans": context.get("remaining_scans", -1)
            }
            
        # 3. Standard screenshot transaction layout verification
        scan_response = await service.execute_full_scan(file_bytes)
        
        if not context.get("is_authenticated"):
            scan_response.anonymous_session_id = context.get("uid")
        scan_response.remaining_scans = context.get("remaining_scans", -1)
        
        response.headers["X-Anonymous-Session-ID"] = context.get("uid")
        response.headers["X-Remaining-Scans"] = str(context.get("remaining_scans", -1))
        
        return {
            "file_type": "screenshot",
            "screenshot_result": scan_response.model_dump(),
            "anonymous_session_id": context.get("uid"),
            "remaining_scans": context.get("remaining_scans", -1)
        }
    except Exception as e:
        print(f"Unified Scanner Pipeline Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute unified scan pipeline: {str(e)}"
        )
