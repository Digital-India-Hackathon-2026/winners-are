import httpx
import asyncio
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from backend.core.config import settings
from backend.integrations.supabase_client import get_supabase_client

API_URL = "https://safebrowsing.googleapis.com/v4/threatMatches:find"

def _read_from_cache(urls: List[str]) -> Dict[str, Dict[str, Any]]:
    """Read threat status for a list of URLs from Supabase cache (must be run via to_thread)."""
    client = get_supabase_client()
    if not client:
        return {}
    try:
        now = datetime.now(timezone.utc)
        ttl_limit = now - timedelta(hours=24)
        
        # Query where url in list and checked_at >= 24h limit
        response = client.table("safe_browsing_cache") \
            .select("*") \
            .in_("url", urls) \
            .gte("checked_at", ttl_limit.isoformat()) \
            .execute()
            
        cached = {}
        for row in response.data:
            cached[row["url"]] = {
                "is_threat": row["is_threat"],
                "threat_type": row["threat_type"]
            }
        return cached
    except Exception as e:
        print(f"[SAFE-BROWSING] Cache read error: {e}")
        return {}

def _write_to_cache(records: List[Dict[str, Any]]) -> None:
    """Upsert threat status records into Supabase cache (must be run via to_thread)."""
    client = get_supabase_client()
    if not client:
        return
    try:
        client.table("safe_browsing_cache").upsert(records).execute()
        print(f"[SAFE-BROWSING] Cached {len(records)} URL check results to database.")
    except Exception as e:
        print(f"[SAFE-BROWSING] Cache write error: {e}")


async def check_urls(urls: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Check if a list of URLs are flagged threats by Google Safe Browsing.
    Uses Supabase caching with a 24-hour TTL. Fail-open model.
    """
    if not urls:
        return {}

    # Unique, cleaned URL list
    unique_urls = list(set([u.strip() for u in urls if u and u.strip()]))
    if not unique_urls:
        return {}

    results: Dict[str, Dict[str, Any]] = {}

    # 1. Read from Supabase Cache
    cached_results = await asyncio.to_thread(_read_from_cache, unique_urls)
    for url, data in cached_results.items():
        results[url] = data

    # Find cache misses
    missed_urls = [u for u in unique_urls if u not in results]
    if not missed_urls:
        return results

    # 2. Query Google Safe Browsing for cache misses in batches of 500
    api_key = settings.GOOGLE_SAFE_BROWSING_API_KEY
    if not api_key:
        print("[SAFE-BROWSING] Warning: GOOGLE_SAFE_BROWSING_API_KEY is not set. Failing open.")
        for url in missed_urls:
            results[url] = {"is_threat": None, "threat_type": None}
        return results

    batch_size = 500
    cache_to_write: List[Dict[str, Any]] = []

    async with httpx.AsyncClient(timeout=10.0) as client:
        for i in range(0, len(missed_urls), batch_size):
            batch = missed_urls[i : i + batch_size]
            
            payload = {
                "client": {
                    "clientId": "trustlayer-ai",
                    "clientVersion": "1.0.0"
                },
                "threatInfo": {
                    "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": url} for url in batch]
                }
            }

            try:
                url_with_key = f"{API_URL}?key={api_key}"
                response = await client.post(url_with_key, json=payload)
                
                if response.status_code != 200:
                    print(f"[SAFE-BROWSING] API error: status {response.status_code}, response: {response.text}")
                    # Fail open for the batch
                    for url in batch:
                        results[url] = {"is_threat": None, "threat_type": None}
                    continue

                response_data = response.json()
                matches = response_data.get("matches", [])
                
                # Map matches by URL
                threat_map = {}
                for match in matches:
                    threat_url = match.get("threat", {}).get("url")
                    if threat_url:
                        threat_map[threat_url] = match.get("threatType", "SUSPICIOUS")

                # Populate results and build cache records
                now_str = datetime.now(timezone.utc).isoformat()
                for url in batch:
                    if url in threat_map:
                        is_threat = True
                        threat_type = threat_map[url]
                    else:
                        is_threat = False
                        threat_type = None

                    results[url] = {"is_threat": is_threat, "threat_type": threat_type}
                    cache_to_write.append({
                        "url": url,
                        "is_threat": is_threat,
                        "threat_type": threat_type,
                        "checked_at": now_str
                    })

            except Exception as e:
                print(f"[SAFE-BROWSING] API request failed: {e}. Failing open.")
                for url in batch:
                    results[url] = {"is_threat": None, "threat_type": None}

    # 3. Write new lookups back to cache asynchronously
    if cache_to_write:
        await asyncio.to_thread(_write_to_cache, cache_to_write)

    return results
