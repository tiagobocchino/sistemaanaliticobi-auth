"""
User management routes (admin-only).
"""
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import get_current_admin_user
from src.supabase_client import supabase_admin_client
from src.users.models import UserUpdateRequest

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("")
async def list_users(_admin=Depends(get_current_admin_user)):
    """List all users (admin only)."""
    for table in ("usuarios", "users"):
        try:
            response = supabase_admin_client.table(table).select("*").execute()
            if response.data is not None:
                return response.data
        except Exception:
            continue
    return []


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    payload: UserUpdateRequest,
    _admin=Depends(get_current_admin_user),
):
    """Update user fields (admin only)."""
    update_payload = {
        k: v for k, v in payload.model_dump().items() if v is not None
    }

    if not update_payload:
        return {"message": "No changes"}

    for table in ("usuarios", "users"):
        try:
            response = (
                supabase_admin_client.table(table)
                .update(update_payload)
                .eq("id", user_id)
                .execute()
            )
            if response.data is not None:
                return response.data
        except Exception:
            continue

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
