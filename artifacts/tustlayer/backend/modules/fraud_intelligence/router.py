from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from backend.modules.fraud_intelligence.schemas import FraudMatchResult
from backend.modules.fraud_intelligence.service import FraudIntelligenceService, get_fraud_intelligence_service
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/fraud-intelligence", tags=["Fraud Intelligence"])

@router.post("/scan", response_model=FraudMatchResult)
async def scan_payment_proof(
    file: UploadFile = File(...),
    service: FraudIntelligenceService = Depends(get_fraud_intelligence_service),
    # current_user: dict = Depends(get_current_user) # Disabled for easy hackathon testing
):
    """
    Scans an uploaded payment screenshot against known fraud fingerprints using perceptual hashing.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image."
        )
        
    image_bytes = await file.read()
    
    try:
        result = await service.scan_image(image_bytes)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while scanning the image."
        )
