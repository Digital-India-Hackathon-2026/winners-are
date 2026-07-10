from typing import List, Optional
from backend.modules.fraud_intelligence.schemas import FraudFingerprint, FraudMatchResult
from backend.modules.fraud_intelligence.phash_matcher import FraudIntelligenceEngine
from backend.core.database import get_db
from datetime import datetime

class FraudIntelligenceService:
    def __init__(self, db_client=None):
        self.engine = FraudIntelligenceEngine(exact_match_threshold=5)
        # Obtain client either via dependency injection or default DB manager
        try:
            self.db = db_client if db_client is not None else get_db()
        except Exception as e:
            print(f"Failed to initialize Supabase client: {e}")
            self.db = None
            
        # HACKATHON STUB: In-memory fallback database of known scam templates
        self._mock_database = [
            FraudFingerprint(
                id="mock-1",
                phash="9e3e3e3e3e3e3e3e", # Example dummy hash
                fraud_type="Cloned Paytm Receipt",
                description="Common template used in Facebook marketplace scams."
            ),
            FraudFingerprint(
                id="mock-2",
                phash="ff00ff00ff00ff00", # Example dummy hash
                fraud_type="Fake PhonePe Transfer",
                description="Spoofed app screenshot."
            )
        ]

    async def _fetch_known_fingerprints(self) -> List[FraudFingerprint]:
        """
        Fetches known scam templates from Supabase. If Supabase is offline/unconfigured,
        falls back gracefully to the in-memory mock dataset.
        """
        if not self.db:
            print("Supabase client not configured. Falling back to local mock data.")
            return self._mock_database
            
        try:
            # Select all records from the 'fraud_fingerprints' table
            response = self.db.table("fraud_fingerprints").select("*").execute()
            
            fingerprints = []
            for row in response.data:
                fingerprints.append(FraudFingerprint(
                    id=str(row.get("id")),
                    phash=row.get("phash"),
                    fraud_type=row.get("fraud_type"),
                    description=row.get("description", "")
                ))
            
            # If DB is empty, use the mock database to ensure a functional demo
            if not fingerprints:
                print("Supabase table 'fraud_fingerprints' is empty. Injecting mocks to keep scan working.")
                return self._mock_database
                
            return fingerprints
        except Exception as e:
            print(f"Supabase query failed: {e}. Gracefully falling back to in-memory mocks.")
            return self._mock_database

    def add_known_scam(self, fingerprint: FraudFingerprint):
        """Adds a scam template to Supabase, or in-memory mock if unconfigured."""
        if self.db:
            try:
                self.db.table("fraud_fingerprints").insert({
                    "phash": fingerprint.phash,
                    "fraud_type": fingerprint.fraud_type,
                    "description": fingerprint.description
                }).execute()
                print(f"Successfully inserted scam template to Supabase: {fingerprint.fraud_type}")
                return
            except Exception as e:
                print(f"Failed to insert scam template to Supabase: {e}. Adding to local mock memory instead.")
        
        self._mock_database.append(fingerprint)

    async def scan_image(self, image_bytes: bytes) -> FraudMatchResult:
        """
        Core service method to orchestrate the intelligence scan.
        """
        # 1. Generate Fingerprint
        input_hash = self.engine.generate_phash(image_bytes)
        
        # 2. Fetch templates dynamically from Supabase (or fallback)
        known_fingerprints = await self._fetch_known_fingerprints()
        
        # 3. Find Matches in DB
        matches = self.engine.find_matches(input_hash, known_fingerprints)
        
        # 4. Construct Result
        if not matches:
            return FraudMatchResult(
                fingerprint_match=False,
                match_confidence=0.0,
                match_count=0,
                top_matches=[]
            )
            
        best_match = matches[0]
        
        return FraudMatchResult(
            fingerprint_match=True,
            match_confidence=best_match.match_confidence,
            match_count=len(matches),
            fraud_type=best_match.fraud_type,
            top_matches=matches
        )

# Dependency injection helper
def get_fraud_intelligence_service() -> FraudIntelligenceService:
    return FraudIntelligenceService()

