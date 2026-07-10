from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from backend.modules.ocr.schemas import OCRResult
from backend.modules.ocr.service import OCRService, get_ocr_service

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR Extraction"])

@router.post("/extract", response_model=OCRResult)
async def extract_text_from_proof(
    file: UploadFile = File(...),
    service: OCRService = Depends(get_ocr_service)
):
    """
    Extracts structured payment data from a screenshot. 
    Uses Tesseract with an automatic AI Vision fallback for low-confidence images.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image."
        )
        
    image_bytes = await file.read()
    
    try:
        result = await service.extract_payment_proof(image_bytes)
        return result
    except Exception as e:
        print(f"OCR Pipeline Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during OCR extraction."
        )
