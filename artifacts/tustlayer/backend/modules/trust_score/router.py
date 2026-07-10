from fastapi import APIRouter, Depends, HTTPException, status
from backend.modules.trust_score.schemas import TrustScoreInput, TrustScoreResult
from backend.modules.trust_score.service import FinalDecisionAssembler, get_final_decision_assembler

router = APIRouter(prefix="/api/v1/trust-score", tags=["Trust Score"])

@router.post("/evaluate", response_model=TrustScoreResult)
async def evaluate_trust_score(
    payload: TrustScoreInput,
    assembler: FinalDecisionAssembler = Depends(get_final_decision_assembler)
):
    """
    Calculates the final deterministic trust score based on inputs from OCR, Fraud Intelligence, and visual heuristics.
    """
    try:
        result = await assembler.evaluate(payload)
        return result
    except Exception as e:
        print(f"Trust Score Engine Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assemble final trust score."
        )
