"""
Pydantic models for authentication flows.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserSignUp(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: Optional[str] = None
    cargo_id: Optional[str] = None
    divisao_id: Optional[str] = None


class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    cargo_id: Optional[str] = None
    divisao_id: Optional[str] = None
    created_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    refresh_token: str
    user: UserResponse


class SignUpResponse(BaseModel):
    message: str
    requires_email_confirmation: bool
    access_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_in: Optional[int] = None
    refresh_token: Optional[str] = None
    user: Optional[UserResponse] = None


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordUpdateRequest(BaseModel):
    new_password: str = Field(min_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str
