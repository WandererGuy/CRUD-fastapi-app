from typing import AsyncGenerator

from langchain_community.utilities import SQLDatabase
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
import redis.asyncio as aioredis

from settings import settings as st


class Base(DeclarativeBase):
    pass


def get_db() -> SQLDatabase:
    return SQLDatabase.from_uri(st.pg_url.get_secret_value())


def create_async_pg_engine():
    # Convert PostgreSQL URL to async format
    pg_url = st.pg_url.get_secret_value()
    async_url = pg_url.replace("postgresql://", "postgresql+asyncpg://")

    async_engine = create_async_engine(
        async_url,
        pool_size=st.pool_size,
        max_overflow=st.max_overflow,
        pool_recycle=st.pool_recycle,
        echo=False,  # Set to True for SQL query logging in development
        # Enhanced connection pool settings to prevent leaks
        pool_pre_ping=True,  # Validate connections before use
        pool_reset_on_return="commit",  # Reset connection state on return
        # Connection timeout settings (in seconds)
        pool_timeout=st.pool_timeout,  # Wait for connection from pool
        # AsyncPG specific connection arguments
        connect_args={
            # Connection timeout in seconds
            "command_timeout": 60,
            # PostgreSQL server settings
            "server_settings": {
                "application_name": "intrepid-ai-fastapi",
                "statement_timeout": "300s",  # 5 minutes
                "idle_in_transaction_session_timeout": "600s",  # 10 minutes
            },
        },
        # Connection pool event logging for debugging
        # Uncomment these for debugging connection issues:
        # logging_name="sqlalchemy.pool",
        # echo_pool=True,
    )
    return async_engine


# Async engine and session factory
async_engine = create_async_pg_engine()
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

# Use async engine as the default engine
engine = async_engine


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for async database sessions.

    This function provides proper session lifecycle management:
    - Creates session from connection pool
    - Handles exceptions with automatic rollback
    - Ensures session is always closed and returned to pool
    """
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
    except Exception as e:
        if session:
            await session.rollback()
        raise
    finally:
        if session:
            await session.close()


# Redis connection pool
redis_client: aioredis.Redis | None = None


async def init_redis():
    """Initialize Redis connection pool."""
    global redis_client
    redis_client = await aioredis.from_url(
        st.redis_url,
        password=st.redis_password.get_secret_value() if st.redis_password else None,
        encoding="utf-8",
        decode_responses=True,
        max_connections=10,
    )
    return redis_client


async def close_redis():
    """Close Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


async def get_redis() -> aioredis.Redis:
    """
    FastAPI dependency for Redis client.

    Returns the global Redis client instance.
    Must be initialized via init_redis() on app startup.
    """
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() on app startup.")
    return redis_client
