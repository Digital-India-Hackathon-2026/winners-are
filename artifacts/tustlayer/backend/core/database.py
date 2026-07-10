from supabase import Client
from backend.integrations.supabase_client import get_supabase_client

def get_db() -> Client:
    """
    Dependency helper that retrieves a configured Supabase client.
    """
    client = get_supabase_client()
    if client is None:
        # We can raise an error or return None (with warnings handled by integrations/caller)
        pass
    return client
