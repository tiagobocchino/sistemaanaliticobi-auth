"""
Authentication dependencies for FastAPI routes.
"""
from typing import Optional
from fastapi import Header, HTTPException, status

from src.auth.service import auth_service
from src.supabase_client import supabase_admin_client


def _extract_bearer_token(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authenticated")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid authorization header")

    return parts[1]


async def get_current_user(authorization: Optional[str] = Header(default=None)):
    """Return the current authenticated user."""
    token = _extract_bearer_token(authorization)
    user = await auth_service.get_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    return user


async def get_current_admin_user(authorization: Optional[str] = Header(default=None)):
    """
    Ensure current user has admin access.
    Accepts either nivel_acesso >= 5 or role == "admin".
    """
    user = await get_current_user(authorization)

    # Try "usuarios" first (database schema), then fallback to "users" (tests/mocks).
    user_data = None
    for table in ("usuarios", "users"):
        try:
            response = (
                supabase_admin_client.table(table)
                .select("*, cargos(nivel_acesso)")
                .eq("id", user.id)
                .single()
                .execute()
            )
            if response.data:
                user_data = response.data
                break
        except Exception:
            continue

    if not user_data:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    nivel_acesso = None
    cargos = user_data.get("cargos") if isinstance(user_data, dict) else None
    if cargos and isinstance(cargos, dict):
        nivel_acesso = cargos.get("nivel_acesso")

    role = user_data.get("role") if isinstance(user_data, dict) else None

    if role == "admin" or (isinstance(nivel_acesso, int) and nivel_acesso >= 5):
        return user

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


def get_bearer_token(authorization: Optional[str] = Header(default=None)) -> str:
    """Expose bearer token extraction for routes that need it."""
    return _extract_bearer_token(authorization)
