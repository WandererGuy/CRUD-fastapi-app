from sqlalchemy import func, or_, select
from models import Brand
from sqlalchemy.orm import Session
import uuid
from typing import Optional
from schemas import CreateBrandRequest, BrandResponse, UpdateBrandRequest
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import List, Optional

class BrandRepository:

    async def get_by_name_async(self, session: AsyncSession, name: str) -> Optional[Brand]:
        stmt = select(Brand).where(Brand.name == name)
        result = await session.execute(stmt)
        return result.scalars().first()


    async def create_async(self, db: AsyncSession, request: CreateBrandRequest) -> Brand:
        """Create a brand asynchronously."""
        try:
            # Use naive UTC
            current_time = datetime.utcnow()

            brand = Brand(
                id=uuid.uuid4(),
                external_brand_id=request.external_brand_id,
                name=request.name,
                display_name=request.display_name or request.name,
                description=request.description,
                logo_url=request.logo_url,
                is_active=True if request.is_active is None else request.is_active,
                created_at=current_time,
                updated_at=current_time,
            )

            db.add(brand)
            await db.flush()
            return brand
        except Exception as e:
            logger.error(f"Error in create_brand_async: {e}")
            raise


    async def get_list_async(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        query_str: Optional[str] = None,
        is_active: Optional[bool] = None,
        ordering: Optional[list[str]] = None,
    ) -> List[Brand]:
        stmt = select(Brand)
        if query_str:
            stmt = stmt.where(or_(Brand.name.ilike(f"%{query_str}%"), Brand.display_name.ilike(f"%{query_str}%")))

        if is_active is not None:
            stmt = stmt.where(Brand.is_active == is_active)

        # Always sort by created_at descending if no explicit ordering is provided
        if ordering and len(ordering) > 0:
            for order in ordering:
                if order.startswith("-"):
                    field_name = order[1:]
                    if hasattr(Brand, field_name):
                        stmt = stmt.order_by(getattr(Brand, field_name).desc())
                else:
                    if hasattr(Brand, order):
                        stmt = stmt.order_by(getattr(Brand, order).asc())
        # Always add created_at desc as a secondary sort for stability
        stmt = stmt.order_by(Brand.created_at.desc())

        # Defensive: ensure skip/limit are int, not AuthInfo
        if isinstance(skip, int) and skip > 0:
            stmt = stmt.offset(skip)
        if isinstance(limit, int) and limit > 0:
            stmt = stmt.limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def count_list_async(
        self,
        session: AsyncSession,
        query_str: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """
        If user is Super Admin or Brand Admin, count all brands.
        Otherwise, count only brands related to stores the user has access to (via AuthInfo).
        """


        stmt = select(func.count(Brand.id))

        if query_str:
            stmt = stmt.where(or_(Brand.name.ilike(f"%{query_str}%"), Brand.display_name.ilike(f"%{query_str}%")))

        if is_active is not None:
            stmt = stmt.where(Brand.is_active == is_active)

        result = await session.execute(stmt)
        return result.scalar()

    async def get_by_id_async(self, session: AsyncSession, brand_id: uuid.UUID) -> Optional[Brand]:
        """Get a brand by ID asynchronously."""
        stmt = select(Brand).where(Brand.id == brand_id)
        result = await session.execute(stmt)
        return result.scalars().first()

    async def update_async(self, db: AsyncSession, brand_id: uuid.UUID, request: UpdateBrandRequest) -> Optional[Brand]:
        """Update a brand asynchronously."""
        try:
            # Get the existing brand
            brand = await self.get_by_id_async(db, brand_id)
            if not brand:
                return None

            # Update only the fields that are provided
            if request.external_brand_id is not None:
                brand.external_brand_id = request.external_brand_id
            if request.name is not None:
                brand.name = request.name
            if request.display_name is not None:
                brand.display_name = request.display_name
            if request.description is not None:
                brand.description = request.description
            if request.logo_url is not None:
                brand.logo_url = request.logo_url
            if request.is_active is not None:
                brand.is_active = request.is_active

            brand.updated_at = datetime.utcnow()

            await db.flush()
            return brand
        except Exception as e:
            logger.error(f"Error in update_brand_async: {e}")
            raise

    async def delete_async(self, db: AsyncSession, brand_id: uuid.UUID) -> bool:
        """Delete a brand asynchronously."""
        try:
            brand = await self.get_by_id_async(db, brand_id)
            if not brand:
                return False

            await db.delete(brand)
            await db.flush()
            return True
        except Exception as e:
            logger.error(f"Error in delete_brand_async: {e}")
            raise
