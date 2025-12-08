"""
Supabase client configuration
"""
from supabase import create_client, Client
from src.config import get_settings

settings = get_settings()


def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance

    Returns:
        Client: Supabase client configured with anon key
    """
    supabase: Client = create_client(
        settings.supabase_url,
        settings.supabase_anon_key
    )
    return supabase


def get_supabase_admin_client() -> Client:
    """
    Create and return a Supabase admin client instance
    Uses service_role key for admin operations

    Returns:
        Client: Supabase client configured with service role key
    """
    supabase: Client = create_client(
        settings.supabase_url,
        settings.supabase_service_role_key
    )
    return supabase


# Global client instances
supabase_client = get_supabase_client()
supabase_admin_client = get_supabase_admin_client()
