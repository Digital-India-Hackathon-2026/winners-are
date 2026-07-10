from fastapi import Request, Header, HTTPException, status
import uuid
from typing import Optional
from backend.core.security import verify_token
from backend.modules.scan_pipeline.session import (
    get_anonymous_session,
    create_anonymous_session,
    increment_session_scan_count
)

async def get_session_or_user(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_anonymous_session_id: Optional[str] = Header(None)
) -> dict:
    """
    Optional auth dependency. 
    1. If authorization header is present and valid, returns the user credentials (no scan limits).
    2. Otherwise, returns/generates an anonymous guest session ID and enforces a 5-scan rate limit.
    """
    
    # 1. Parse and verify Bearer Token if present
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1]
        try:
            user_data = verify_token(token)
            return {
                "uid": user_data.get("uid", "mock-user-id"),
                "is_authenticated": True,
                "remaining_scans": -1
            }
        except Exception:
            # Fall back to anonymous session instead of failing outright, as auth is optional
            pass
            
    # 2. Check or generate Anonymous Session ID
    session_id = x_anonymous_session_id
    if not session_id or session_id.strip() == "":
        session_id = str(uuid.uuid4())
        
    # Check if session exists, if not create it
    session = get_anonymous_session(session_id)
    if not session:
        create_anonymous_session(session_id)
        current_scans = 0
    else:
        current_scans = session.get("scan_count", 0)
        
    # Enforce 5 guest scans limit
    if current_scans >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Scan limit exceeded for guest session. Please sign up or authenticate to scan more documents."
        )
        
    # Increment count
    updated_scans = increment_session_scan_count(session_id)
    
    return {
        "uid": session_id,
        "is_authenticated": False,
        "remaining_scans": max(0, 5 - updated_scans)
    }
