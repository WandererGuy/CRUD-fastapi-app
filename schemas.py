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
