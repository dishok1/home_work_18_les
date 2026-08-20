import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool
from app.user_models import Base, User, AccessToken


DATABASE_URL = settings.DATABASE_URL


engine = create_async_engine(DATABASE_URL, poolclass=NullPool, pool_pre_ping=True)
async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


# Обов'язково перевірте, щоб функція виглядала саме так:
async def create_db_and_tables():
    async with engine.begin() as conn:
        # Для асинхронного двигуна створювати таблиці потрібно ТІЛЬКИ через run_sync!
        await conn.run_sync(Base.metadata.create_all)



async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def drop_all_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
