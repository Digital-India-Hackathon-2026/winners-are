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
