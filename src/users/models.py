"""
Pydantic models for user management.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserSummary(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    cargo_id: Optional[str] = None
    divisao_id: Optional[str] = None
    role: Optional[str] = None


class UserUpdateRequest(BaseModel):
    cargo: Optional[str] = None
    divisao: Optional[str] = None
    role: Optional[str] = None
    cargo_id: Optional[str] = None
    divisao_id: Optional[str] = None
