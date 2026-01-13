"""
Authentication routes.
"""
from fastapi import APIRouter, HTTPException, status, Depends

from src.auth.models import (
    UserSignUp,
    UserSignIn,
    RefreshTokenRequest,
    PasswordResetRequest,
    PasswordUpdateRequest,
)
from src.auth.service import auth_service, AuthenticationError
from src.auth.dependencies import get_current_user, get_bearer_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignUp):
    """Register a new user."""
    try:
        result = await auth_service.sign_up(user_data)
        if result.requires_email_confirmation:
            return {
                "message": result.message,
                "requires_email_confirmation": True,
                "user": result.user.model_dump() if result.user else None,
            }
        return {
            "message": result.message,
            "requires_email_confirmation": False,
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
            "token_type": result.token_type,
            "expires_in": result.expires_in,
            "user": result.user.model_dump() if result.user else None,
        }
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/signin")
async def signin(credentials: UserSignIn):
    """Authenticate user and return tokens."""
    try:
        result = await auth_service.sign_in(credentials)
        return result.model_dump()
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(token: str = Depends(get_bearer_token)):
    """Sign out user and invalidate token."""
    success = await auth_service.sign_out(token)
    if success:
        return None
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to sign out")


@router.post("/refresh")
async def refresh_token(payload: RefreshTokenRequest):
    """Refresh access token using refresh token."""
    try:
        result = await auth_service.refresh_token(payload.refresh_token)
        return result.model_dump()
    except AuthenticationError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/me")
async def get_me(current_user=Depends(get_current_user)):
    """Return current user data."""
    return current_user.model_dump()


@router.post("/reset-password")
async def reset_password(payload: PasswordResetRequest):
    """Request password reset."""
    success = await auth_service.reset_password(payload)
    return {"success": success}


@router.post("/update-password")
async def update_password(
    payload: PasswordUpdateRequest,
    token: str = Depends(get_bearer_token),
    _current_user=Depends(get_current_user),
):
    """Update password for current user."""
    success = await auth_service.update_password(token, payload)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to update password")
    return {"success": True}
