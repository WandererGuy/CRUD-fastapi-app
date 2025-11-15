from fastapi import FastAPI, Depends, HTTPException, status, Query
import uuid
from fastapi import APIRouter, Body, Depends, HTTPException, status, UploadFile, File
from database import get_async_db
from exception import ValidationException, ServiceException, IntegrityError, to_http_exception
from typing import Annotated
from schemas import CreateBrandRequest, BrandResponse, UpdateBrandRequest
from service import BrandService
# ---------- Initialize ----------
app = FastAPI(title="Brand CRUD API (Class-Based)")


from loguru import logger


def get_brand_service() -> BrandService:
    """Dependency to get BrandService instance."""
    return BrandService()


from sqlalchemy.ext.asyncio import AsyncSession
BrandServiceDep = Annotated[BrandService, Depends(get_brand_service)]
DatabaseDep = Annotated[AsyncSession, Depends(get_async_db)]


router = APIRouter(
    prefix="/brands",
    tags=["Brands"],
    responses={
        400: {"description": "Bad request"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "Not found"},
        422: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)

@router.post(
    "",
    response_model=BrandResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create brand",
    description="Create a new brand in the system",
    response_description="The created brand information",
)
async def create_brand(
    request: CreateBrandRequest,
    brand_service: BrandServiceDep,
    db: DatabaseDep
    ) -> BrandResponse:
    """
    Create a new brand.

    Args:
        request: Brand creation request with name, description, and other brand info
        brand_service: Injected brand service
        db: Injected async database session

    Returns:
        BrandResponse: Created brand information

    Raises:
        HTTPException: 400 for validation errors (duplicate name), 500 for internal errors

    Notes:
        - Brand name must be unique in the system
        - All new brands are created with is_active=True by default
        - External brand ID is optional for integration purposes
    """
    logger.info (f"Received request to create brand: {request}")
    try:
        response = await brand_service.create_brand(request, db)
        return response

    except (ValidationException, ServiceException) as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create brand due to internal error"
        )
    


from schemas import ListBrandParams, ListBrandsResponse


@router.get(
    "",
    response_model=ListBrandsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get all brands",
    description="Retrieve a paginated list of brands with optional filtering and search",
    response_description="Paginated list of brands with total count",
)
async def get_brands(
    brand_service: BrandServiceDep,
    db: DatabaseDep,
    params: ListBrandParams = Depends()
) -> ListBrandsResponse:
    """
    Get paginated list of brands with filtering.

    Args:
        params: Query parameters for pagination, filtering, and search
        brand_service: Injected brand service
        db: Injected async database session
    Returns:
        ListBrandsResponse: Paginated list of brands

    Raises:
        HTTPException: 400 for validation errors, 401 for auth errors, 500 for internal errors

    Query Parameters:
        - page: Page number (default: 1)
        - pagesize: Items per page (default: 10, max: 100)
        - q: Search query (searches in name and display name)
        - is_active: Filter by active status
        - ordering: Sort fields (default: ["-created_at"])
    """
    try:
        response = await brand_service.get_list_brands(params, db)
        return response

    except (ValidationException, ServiceException) as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve brands due to internal error"
        )


@router.get(
    "/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
    summary="Get brand by ID",
    description="Retrieve a single brand by its ID",
    response_description="Brand information",
)
async def get_brand_by_id(
    brand_id: uuid.UUID,
    brand_service: BrandServiceDep,
    db: DatabaseDep
) -> BrandResponse:
    """
    Get a brand by ID.

    Args:
        brand_id: UUID of the brand to retrieve
        brand_service: Injected brand service
        db: Injected async database session

    Returns:
        BrandResponse: Brand information

    Raises:
        HTTPException: 404 if brand not found, 500 for internal errors
    """
    try:
        response = await brand_service.get_brand_by_id(brand_id, db)
        return response

    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve brand due to internal error"
        )


@router.put(
    "/{brand_id}",
    response_model=BrandResponse,
    status_code=status.HTTP_200_OK,
    summary="Update brand",
    description="Update an existing brand",
    response_description="Updated brand information",
)
async def update_brand(
    brand_id: uuid.UUID,
    request: UpdateBrandRequest,
    brand_service: BrandServiceDep,
    db: DatabaseDep
) -> BrandResponse:
    """
    Update a brand.

    Args:
        brand_id: UUID of the brand to update
        request: Brand update request with fields to update
        brand_service: Injected brand service
        db: Injected async database session

    Returns:
        BrandResponse: Updated brand information

    Raises:
        HTTPException: 404 if brand not found, 400 for validation errors, 500 for internal errors
    """
    logger.info(f"Received request to update brand {brand_id}: {request}")
    try:
        response = await brand_service.update_brand(brand_id, request, db)
        return response

    except ValidationException as e:
        error_msg = str(e)
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)
    except ServiceException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update brand due to internal error"
        )


@router.delete(
    "/{brand_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete brand",
    description="Delete a brand from the system",
    response_description="No content on successful deletion",
)
async def delete_brand(
    brand_id: uuid.UUID,
    brand_service: BrandServiceDep,
    db: DatabaseDep
) -> None:
    """
    Delete a brand.

    Args:
        brand_id: UUID of the brand to delete
        brand_service: Injected brand service
        db: Injected async database session

    Raises:
        HTTPException: 404 if brand not found, 500 for internal errors
    """
    logger.info(f"Received request to delete brand {brand_id}")
    try:
        await brand_service.delete_brand(brand_id, db)

    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ServiceException as e:
        raise to_http_exception(e)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete brand due to internal error"
        )