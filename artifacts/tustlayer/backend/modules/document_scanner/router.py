from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.modules.document_scanner.service import get_document_scanner_service
from backend.modules.document_scanner.schemas import DocumentThreatResult

router = APIRouter(prefix="/api/v1/document", tags=["Document Scanner"])

ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "application/pdf",
}


@router.post("/scan", response_model=DocumentThreatResult)
async def scan_document(file: UploadFile = File(...)):
    """
    Scan a document (image or PDF) for embedded threats:
    - Steganography (LSB analysis)
    - Phishing URLs
    - PDF JavaScript / auto-actions
    - Embedded files
    """
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: image/*, application/pdf"
        )

    contents = await file.read()
    if len(contents) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    service = get_document_scanner_service()
    return await service.scan(contents, file.content_type or "application/octet-stream")
