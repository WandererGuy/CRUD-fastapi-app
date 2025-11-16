from pydantic import BaseModel, Field
from fastapi import Query

import uuid
from datetime import datetime
from typing import Optional

class BrandResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Brand ID")
    external_brand_id: Optional[str] = Field(None, description="External brand ID")
    name: str = Field(..., description="Brand name")
    display_name: Optional[str] = Field(None, description="Brand display name")
    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[str] = Field(None, description="Brand logo URL")
    is_active: bool = Field(..., description="Brand active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

class CreateBrandRequest(BaseModel):
    external_brand_id: Optional[str] = Field(None, description="External brand ID")
    name: str = Field(..., min_length=1, max_length=100, description="Brand name")
    display_name: Optional[str] = Field(None, max_length=200, description="Brand display name")
    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[str] = Field(None, max_length=255, description="Brand logo URL")
    is_active: bool = Field(True, description="Brand active status")


class UpdateBrandRequest(BaseModel):
    external_brand_id: Optional[str] = Field(None, description="External brand ID")
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Brand name")
    display_name: Optional[str] = Field(None, max_length=200, description="Brand display name")
    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[str] = Field(None, max_length=255, description="Brand logo URL")
    is_active: Optional[bool] = Field(None, description="Brand active status")


class BrandResponse(BaseModel):
    id: uuid.UUID = Field(..., description="Brand ID")
    external_brand_id: Optional[str] = Field(None, description="External brand ID")
    name: str = Field(..., description="Brand name")
    display_name: Optional[str] = Field(None, description="Brand display name")
    description: Optional[str] = Field(None, description="Brand description")
    logo_url: Optional[str] = Field(None, description="Brand logo URL")
    is_active: bool = Field(..., description="Brand active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ListBrandParams(BaseModel):
    page: Optional[int] = Field(Query(1, ge=1, description="Page number"))
    pagesize: Optional[int] = Field(Query(10, ge=1, le=100, description="Items per page"))
    q: Optional[str] = Field(Query(None, description="Search query for name or display name"))
    is_active: Optional[bool] = Field(Query(None, description="Filter by active status"))
    ordering: Optional[list[str]] = Field(
        Query(["-created_at"], description="Ordering fields", example=["name", "-created_at"])
    )
    sig: Optional[str] = Field(None, description="CMS access public key")


class ListBrandsResponse(BaseModel):
    total: int = Field(..., description="Total number of brands")
    data: list[BrandResponse] = Field(..., description="List of brands")


# ==================== User Authentication Schemas ====================

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserResponse(BaseModel):
    id: uuid.UUID = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    email: str = Field(..., description="Email address")
    is_active: bool = Field(..., description="User active status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class LoginRequest(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    username: str | None = None
    user_id: uuid.UUID | None = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")
