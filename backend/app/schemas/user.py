from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    full_name: str = Field(
        min_length=2,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str = "user"
    is_admin: bool = False
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminUserResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    role: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    materials_count: int = 0

    model_config = ConfigDict(
        from_attributes=True,
    )


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int
    page: int
    limit: int
    pages: int


class UserStatusUpdate(BaseModel):
    is_active: bool


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"