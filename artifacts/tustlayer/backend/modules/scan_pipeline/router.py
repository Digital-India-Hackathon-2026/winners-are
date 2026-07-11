from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Response, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import httpx
from backend.modules.scan_pipeline.schemas import FinalScanResponse
from backend.modules.scan_pipeline.service import ScanPipelineService, get_scan_pipeline_service
from backend.modules.scan_pipeline.middleware import get_session_or_user

router = APIRouter(prefix="/api/v1/scan", tags=["Scan Pipeline"])

async def get_bytes(file: Optional[UploadFile] = File(None), file_url: Optional[str] = Form(None)):
    if file_url:
        async with httpx.AsyncClient() as client:
            resp = await client.get(file_url)
            if resp.status_code != 200:
                raise HTTPException(status_code=400, detail="Could not download file from URL")
            return resp.content
    if file:
        return await file.read()
    raise HTTPException(status_code=400, detail="Either file or file_url must be provided")

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


class MessageScanRequest(BaseModel):
    message: str

@router.post("/message")
async def execute_message_scan(
    payload: MessageScanRequest,
    context: dict = Depends(get_session_or_user)
):
    """
    Plain text, WhatsApp, SMS message threat scanner endpoint.
    Runs language, URL, phone, UPI, email, keyword analyses, reputation lookups,
    and returns a structured safety summary + WhatsApp formatted response.
    """
    from backend.modules.message_scanner.service import get_message_scanner_service
    service = get_message_scanner_service()
    res = await service.scan_message(payload.message)
    return res


@router.post("/unified")
async def execute_unified_scan(
    response: Response,
    file: Optional[UploadFile] = File(None),
    file_url: Optional[str] = Form(None),
    service: ScanPipelineService = Depends(get_scan_pipeline_service),
    context: dict = Depends(get_session_or_user)
):
    """
    Unified entrypoint for all verification methods (image, PDF, QR).
    Detects the file type and routes it dynamically to DocumentScannerService,
    QRInspectorService, or the standard transaction image verification pipeline.
    """
    try:
        if file_url:
            async with httpx.AsyncClient() as client:
                download_resp = await client.get(file_url)
                if download_resp.status_code != 200:
                    raise HTTPException(status_code=400, detail="Failed to fetch file from storage URL.")
                file_bytes = download_resp.content
                filename = file_url.split("/")[-1].split("?")[0]
                content_type = download_resp.headers.get("content-type", "")
                is_document = (
                    "pdf" in content_type.lower() or 
                    "word" in content_type.lower() or 
                    "officedocument" in content_type.lower() or 
                    filename.lower().endswith((".pdf", ".doc", ".docx", ".docm")) or 
                    file_bytes[:4] == b"%PDF"
                )
        else:
            if not file:
                raise HTTPException(status_code=400, detail="Either file or file_url must be provided.")
            filename = file.filename or ""
            content_type = file.content_type or ""
            
            # Read a small chunk to check PDF magic bytes safely
            header_chunk = await file.read(4)
            is_document = (
                "pdf" in content_type.lower() or 
                "word" in content_type.lower() or 
                "officedocument" in content_type.lower() or 
                filename.lower().endswith((".pdf", ".doc", ".docx", ".docm")) or 
                header_chunk == b"%PDF"
            )
            
            # Reset pointer for full read
            await file.seek(0)
            file_bytes = await file.read()
        
        # 1. Document routing (PDF, Word docs)
        if is_document:
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
        try:
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
        except HTTPException as he:
            if he.status_code == 422:
                # Fallback: Treat as a general media/document threat scan
                from backend.modules.document_scanner.service import get_document_scanner_service
                doc_service = get_document_scanner_service()
                res = await doc_service.scan(file_bytes, content_type or "image/png")
                return {
                    "file_type": "pdf", # Frontend renders document results under 'pdf' key
                    "document_result": res.model_dump(),
                    "anonymous_session_id": context.get("uid"),
                    "remaining_scans": context.get("remaining_scans", -1)
                }
            raise he
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Unified Scanner Pipeline Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute unified scan pipeline: {str(e)}"
        )
