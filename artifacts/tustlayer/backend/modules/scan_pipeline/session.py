import threading
from datetime import datetime, timezone
from typing import Optional
from backend.core.database import get_db

# Thread-safe in-memory cache fallback
_in_memory_sessions = {}
_lock = threading.Lock()

def get_anonymous_session(session_id: str) -> Optional[dict]:
    """
    Retrieves anonymous session metadata. Checks Supabase table 'anonymous_sessions' first.
    Falls back gracefully to thread-safe in-memory dictionary.
    """
    db = None
    try:
        db = get_db()
    except Exception as e:
        print(f"Database client fetch failed: {e}. Using in-memory store.")
    
    if db:
        try:
            response = db.table("anonymous_sessions").select("*").eq("id", session_id).execute()
            if response.data:
                row = response.data[0]
                return {
                    "id": str(row.get("id")),
                    "scan_count": int(row.get("scan_count", 0)),
                    "last_scan_at": row.get("last_scan_at")
                }
        except Exception as e:
            print(f"Supabase fetch session error: {e}. Falling back to in-memory store.")

    with _lock:
        return _in_memory_sessions.get(session_id)

def create_anonymous_session(session_id: str) -> dict:
    """
    Creates a new anonymous session. Inserts into Supabase 'anonymous_sessions' first.
    Falls back gracefully to thread-safe in-memory dictionary.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    session_data = {
        "id": session_id,
        "scan_count": 0,
        "last_scan_at": now_str
    }
    
    db = None
    try:
        db = get_db()
    except Exception as e:
        print(f"Database client fetch failed: {e}. Using in-memory store.")

    if db:
        try:
            db.table("anonymous_sessions").insert({
                "id": session_id,
                "scan_count": 0,
                "last_scan_at": now_str
            }).execute()
            return session_data
        except Exception as e:
            print(f"Supabase insert session error: {e}. Saving to in-memory store.")

    with _lock:
        _in_memory_sessions[session_id] = session_data
        return session_data

def increment_session_scan_count(session_id: str) -> int:
    """
    Increments scan count for an anonymous session. Checks Supabase first,
    then falls back to in-memory dictionary. Returns updated scan count.
    """
    db = None
    try:
        db = get_db()
    except Exception as e:
        print(f"Database client fetch failed: {e}. Using in-memory store.")

    now_str = datetime.now(timezone.utc).isoformat()

    if db:
        try:
            # First fetch current scan count
            response = db.table("anonymous_sessions").select("scan_count").eq("id", session_id).execute()
            if response.data:
                current_count = int(response.data[0].get("scan_count", 0))
                new_count = current_count + 1
                db.table("anonymous_sessions").update({
                    "scan_count": new_count,
                    "last_scan_at": now_str
                }).eq("id", session_id).execute()
                return new_count
            else:
                # If not found in DB but DB exists, create and set scan_count to 1
                db.table("anonymous_sessions").insert({
                    "id": session_id,
                    "scan_count": 1,
                    "last_scan_at": now_str
                }).execute()
                return 1
        except Exception as e:
            print(f"Supabase update scan count error: {e}. Falling back to in-memory store.")

    with _lock:
        session = _in_memory_sessions.get(session_id)
        if session:
            session["scan_count"] += 1
            session["last_scan_at"] = now_str
            return session["scan_count"]
        else:
            _in_memory_sessions[session_id] = {
                "id": session_id,
                "scan_count": 1,
                "last_scan_at": now_str
            }
            return 1
