"""
Seeding script to populate the PostgreSQL database with example brand data.

Usage:
    python seed.py
"""
import asyncio
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from database import AsyncSessionLocal
from models import Brand


async def clear_brands(session: AsyncSession):
    """Clear all existing brands from the database."""
    logger.info("Clearing existing brands...")
    from sqlalchemy import delete
    await session.execute(delete(Brand))
    await session.commit()
    logger.info("Existing brands cleared")


async def seed_brands(session: AsyncSession):
    """Seed the database with example brand data."""
    logger.info("Seeding brands...")

    example_brands = [
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-001",
            name="apple",
            display_name="Apple Inc.",
            description="Technology company specializing in consumer electronics, software, and services",
            logo_url="https://example.com/logos/apple.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-002",
            name="nike",
            display_name="Nike",
            description="Global athletic footwear and apparel company",
            logo_url="https://example.com/logos/nike.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-003",
            name="samsung",
            display_name="Samsung Electronics",
            description="Multinational electronics and technology company",
            logo_url="https://example.com/logos/samsung.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-004",
            name="coca_cola",
            display_name="The Coca-Cola Company",
            description="Beverage company known for soft drinks and other beverages",
            logo_url="https://example.com/logos/coca-cola.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-005",
            name="amazon",
            display_name="Amazon",
            description="E-commerce and cloud computing company",
            logo_url="https://example.com/logos/amazon.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-006",
            name="google",
            display_name="Google LLC",
            description="Technology company specializing in internet services and products",
            logo_url="https://example.com/logos/google.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-007",
            name="microsoft",
            display_name="Microsoft Corporation",
            description="Technology company developing software, hardware, and cloud services",
            logo_url="https://example.com/logos/microsoft.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-008",
            name="starbucks",
            display_name="Starbucks Corporation",
            description="Coffeehouse chain and coffee roasting company",
            logo_url="https://example.com/logos/starbucks.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-009",
            name="tesla",
            display_name="Tesla Inc.",
            description="Electric vehicle and clean energy company",
            logo_url="https://example.com/logos/tesla.png",
            is_active=True,
        ),
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-010",
            name="mcdonalds",
            display_name="McDonald's Corporation",
            description="Fast food restaurant chain",
            logo_url="https://example.com/logos/mcdonalds.png",
            is_active=True,
        ),
        # Example of an inactive brand
        Brand(
            id=uuid.uuid4(),
            external_brand_id="BRAND-999",
            name="oldcompany",
            display_name="Old Company",
            description="Example of an inactive/discontinued brand",
            logo_url="https://example.com/logos/oldcompany.png",
            is_active=False,
        ),
    ]

    # Add all brands to the session
    session.add_all(example_brands)
    await session.commit()

    logger.info(f"Successfully seeded {len(example_brands)} brands")

    # Display seeded brands
    for brand in example_brands:
        logger.info(f"  - {brand.display_name} ({brand.name}) - Active: {brand.is_active}")


async def main():
    """Main function to run the seeding process."""
    logger.info("Starting database seeding process...")

    async with AsyncSessionLocal() as session:
        try:
            # Option to clear existing data (comment out if you want to keep existing data)
            await clear_brands(session)

            # Seed brands
            await seed_brands(session)

            logger.info("Database seeding completed successfully!")

        except Exception as e:
            logger.error(f"Error during seeding: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
