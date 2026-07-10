from pydantic import BaseModel, Field
from typing import Optional, List
import uuid
from datetime import datetime

class FraudFingerprint(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phash: str = Field(..., description="The perceptual hash of the known scam image in hex format")
    fraud_type: str = Field(..., description="The classification of this template (e.g., 'Cloned Template', 'Edited Proof')")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SimilarityScore(BaseModel):
    fingerprint_id: str
    hamming_distance: int
    match_confidence: float = Field(..., ge=0.0, le=1.0)
    fraud_type: str

class FraudMatchResult(BaseModel):
    fingerprint_match: bool
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    match_count: int = 0
    fraud_type: Optional[str] = None
    top_matches: List[SimilarityScore] = []
