from loguru import logger
from exception import ValidationException, ServiceException, IntegrityError, to_http_exception
from schemas import CreateBrandRequest, BrandResponse, UpdateBrandRequest
from repository import BrandRepository
from sqlalchemy.ext.asyncio import AsyncSession
from models import Brand
from schemas import ListBrandParams, ListBrandsResponse
import uuid

from settings import settings as st
from typing import Optional

def get_paging_params(page: Optional[int] = 1, pagesize: Optional[int] = 10) -> tuple[int, int]:
    if not page or not pagesize:
        return -1, -1
    if pagesize > st.max_page_size:
        pagesize = st.max_page_size
    skip = (page - 1) * pagesize
    return skip, pagesize

class BrandService:
    """Brand service with business logic."""

    def __init__(self):
        """Initialize brand service."""
        self.repository = BrandRepository()

    async def create_brand(self, request: CreateBrandRequest, db: AsyncSession) -> BrandResponse:
        """
        Create a new brand.

        Args:
            request: Brand creation request
            db: Async database session

        Returns:
            BrandResponse: Created brand information

        Raises:
            ValidationException: Invalid data or duplicate name
            ServiceException: Database errors
        """
        try:
            # Check for duplicate name
            existing_brand = await self.repository.get_by_name_async(db, request.name)
            if existing_brand:
                raise ValidationException(f"Brand with name '{request.name}' already exists")

            brand = await self.repository.create_async(db, request)
            await db.commit()

            logger.info(f"Created brand: {brand.name} (ID: {brand.id})")
            return self._to_brand_response(brand)

        except ValidationException:
            await db.rollback()
            raise
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error creating brand: {e}")
            raise ValidationException("Brand name must be unique")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create brand: {e}")
            raise ServiceException("Failed to create brand")


    def _to_brand_response(self, brand: Brand) -> BrandResponse:
        """Convert Brand model to response DTO."""
        return BrandResponse(
            id=brand.id,
            external_brand_id=brand.external_brand_id,
            name=brand.name,
            display_name=brand.display_name,
            description=brand.description,
            logo_url=brand.logo_url,
            is_active=brand.is_active,
            created_at=brand.created_at,
            updated_at=brand.updated_at,
        )
    

    async def get_list_brands(self, params: ListBrandParams, db: AsyncSession) -> ListBrandsResponse:
        """
        Get paginated list of brands with filtering.

        Args:
            params: List parameters with pagination and filters
            db: Async database session

        Returns:
            ListBrandsResponse: Paginated list of brands

        Raises:
            ValidationException: Invalid parameters
            ServiceException: Database or service errors
        """
        try:
            skip, limit = get_paging_params(params.page, params.pagesize)
            brands = await self.repository.get_list_async(db, skip, limit, params.q, params.is_active, params.ordering)
            total = await self.repository.count_list_async(db, params.q, params.is_active)

            brand_responses = []
            for brand in brands:
                resp = self._to_brand_response(brand)
                brand_responses.append(resp)

            return ListBrandsResponse(total=total, data=brand_responses)

        except Exception as e:
            logger.error(f"Failed to get brands list: {e}")
            raise ServiceException("Failed to retrieve brands")

    async def get_brand_by_id(self, brand_id: uuid.UUID, db: AsyncSession) -> BrandResponse:
        """
        Get a brand by ID.

        Args:
            brand_id: Brand UUID
            db: Async database session

        Returns:
            BrandResponse: Brand information

        Raises:
            ValidationException: Brand not found
            ServiceException: Database errors
        """
        try:
            brand = await self.repository.get_by_id_async(db, brand_id)
            if not brand:
                raise ValidationException(f"Brand with ID '{brand_id}' not found")

            logger.info(f"Retrieved brand: {brand.name} (ID: {brand.id})")
            return self._to_brand_response(brand)

        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to get brand by ID: {e}")
            raise ServiceException("Failed to retrieve brand")

    async def update_brand(self, brand_id: uuid.UUID, request: UpdateBrandRequest, db: AsyncSession) -> BrandResponse:
        """
        Update a brand.

        Args:
            brand_id: Brand UUID
            request: Brand update request
            db: Async database session

        Returns:
            BrandResponse: Updated brand information

        Raises:
            ValidationException: Brand not found or duplicate name
            ServiceException: Database errors
        """
        try:
            # Check if name is being updated and if it's already taken
            if request.name:
                existing_brand = await self.repository.get_by_name_async(db, request.name)
                if existing_brand and existing_brand.id != brand_id:
                    raise ValidationException(f"Brand with name '{request.name}' already exists")

            brand = await self.repository.update_async(db, brand_id, request)
            if not brand:
                raise ValidationException(f"Brand with ID '{brand_id}' not found")

            await db.commit()

            logger.info(f"Updated brand: {brand.name} (ID: {brand.id})")
            return self._to_brand_response(brand)

        except ValidationException:
            await db.rollback()
            raise
        except IntegrityError as e:
            await db.rollback()
            logger.error(f"Database integrity error updating brand: {e}")
            raise ValidationException("Brand name must be unique")
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update brand: {e}")
            raise ServiceException("Failed to update brand")

    async def delete_brand(self, brand_id: uuid.UUID, db: AsyncSession) -> None:
        """
        Delete a brand.

        Args:
            brand_id: Brand UUID
            db: Async database session

        Raises:
            ValidationException: Brand not found
            ServiceException: Database errors
        """
        try:
            success = await self.repository.delete_async(db, brand_id)
            if not success:
                raise ValidationException(f"Brand with ID '{brand_id}' not found")

            await db.commit()
            logger.info(f"Deleted brand with ID: {brand_id}")

        except ValidationException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to delete brand: {e}")
            raise ServiceException("Failed to delete brand")
