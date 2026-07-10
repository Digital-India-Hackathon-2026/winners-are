from fastapi import APIRouter, File, UploadFile, HTTPException
from backend.modules.qr_inspector.service import get_qr_inspector_service
from backend.modules.qr_inspector.schemas import QRInspectionResult

router = APIRouter(prefix="/api/v1/qr", tags=["QR Inspector"])


@router.post("/inspect", response_model=QRInspectionResult)
async def inspect_qr(file: UploadFile = File(...)):
    """
    Inspect a payment screenshot for QR codes.
    Extracts UPI QR data and performs forensic risk analysis.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    if len(contents) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")
    
    service = get_qr_inspector_service()
    return await service.inspect(contents)
