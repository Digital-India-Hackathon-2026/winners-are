import os
import asyncio
from typing import Any, Dict
from supabase import create_client, Client
from backend.core.config import settings

def get_supabase_client() -> Client:
    url: str = settings.SUPABASE_URL
    key: str = os.getenv("SUPABASE_ANON_KEY") or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY") or settings.SUPABASE_KEY
    if not url or not key or url == "your_supabase_url_here":
        print("[TRUSTLAYER-DEBUG] Warning: Supabase credentials not set.")
        # Return a mock client for hackathon local dev if needed
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"[TRUSTLAYER-DEBUG] Error initializing Supabase client: {e}")
        return None

async def save_scan_result_async(payload: Dict[str, Any]) -> None:
    client = get_supabase_client()
    if not client:
        return
        
    def _save():
        try:
            # Extract high-level fields for easy querying
            trust_score = payload.get("trust_score_data", {}).get("trust_score", 0)
            risk_level = payload.get("trust_score_data", {}).get("risk_level", "UNKNOWN")
            
            ocr_data = payload.get("ocr_data", {}).get("fields", {})
            payment_amount = str(ocr_data.get("payment_amount", ""))
            upi_transaction_id = str(ocr_data.get("upi_transaction_id", ""))
            
            execution_time = payload.get("metadata", {}).get("execution_time_ms", 0)
            session_id = payload.get("anonymous_session_id")
            
            data = {
                "session_id": session_id,
                "success": payload.get("success", False),
                "trust_score": trust_score,
                "risk_level": risk_level,
                "payment_amount": payment_amount,
                "upi_transaction_id": upi_transaction_id,
                "execution_time_ms": execution_time,
                "full_payload": payload
            }
            
            # Insert into 'scans' table
            response = client.table("scans").insert(data).execute()
            print(f"[TRUSTLAYER-DEBUG] Supabase: Successfully saved scan result to database.")
        except Exception as e:
            print(f"[TRUSTLAYER-DEBUG] Supabase: Failed to save scan result: {e}")
            
    # Run the synchronous Supabase client operation in a separate thread
    await asyncio.to_thread(_save)
