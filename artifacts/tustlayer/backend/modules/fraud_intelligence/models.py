from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class FraudFingerprintDB(BaseModel):
    """
    Pydantic schema representing the DB model/table structure in Supabase.
    Table: fraud_fingerprints
    """
    id: str = Field(..., description="UUID or unique text identifier, primary key")
    phash: str = Field(..., description="Perceptual hash of the image in hex format")
    fraud_type: str = Field(..., description="Classification of the fraud template (e.g. 'Cloned Paytm Receipt')")
    description: Optional[str] = Field(None, description="Detailed description of the scam pattern")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="ISO Timestamp of creation")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
                "phash": "9e3e3e3e3e3e3e3e",
                "fraud_type": "Cloned Paytm Receipt",
                "description": "Common template used in marketplace scams.",
                "created_at": "2026-05-24T12:00:00Z"
            }
        }

# SQL schema to run in Supabase SQL editor:
SQL_SCHEMA = """
CREATE TABLE IF NOT EXISTS fraud_fingerprints (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    phash TEXT NOT NULL UNIQUE,
    fraud_type TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert dummy seed data for testing
INSERT INTO fraud_fingerprints (phash, fraud_type, description)
VALUES 
('9e3e3e3e3e3e3e3e', 'Cloned Paytm Receipt', 'Common template used in Facebook marketplace scams.'),
('ff00ff00ff00ff00', 'Fake PhonePe Transfer', 'Spoofed app screenshot.')
ON CONFLICT (phash) DO NOTHING;
"""
