"""
Compatibility wrapper for Supabase client used by legacy imports.
"""
from src.supabase_client import get_supabase_client

__all__ = ["get_supabase_client"]
