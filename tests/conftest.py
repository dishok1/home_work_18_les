import os
import sys
import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)

if project_root not in sys.path:
    sys.path.insert(0, project_root)

os.environ["ENVIRONMENT"] = "testing"

# Тепер ці імпорти спрацюють ідеально
from app.app import app
from app.user_models import Base, User
from app.config import settings
from app.db import get_async_session

DATABASE_URL = settings.DATABASE_URL.replace("localhost", "127.0.0.1")

engine_test = create_async_engine(
    DATABASE_URL, 
    poolclass=StaticPool,
    pool_pre_ping=True,
    echo=False
)
# Знову доступний для імпорту на 5-му рядку вашого test_app.py
async_session_maker = async_sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)

# Перевизначаємо залежність для FastAPI
async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_async_session] = override_get_async_session

# Підготовка бази даних (один раз на всю сесію тестів)
@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Сесійні сховища для передачі токенів між тестами
@pytest.fixture(scope="session")
def token_storage():
    return {}

@pytest.fixture(scope="session")
def user_id_storage():
    return {}

@pytest.fixture(scope="session")
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture(scope="session")
async def get_token(token_storage):
    return token_storage.get("token")

@pytest.fixture(scope="session")
async def get_user_id(user_id_storage):
    return user_id_storage.get("id")

@pytest.fixture(scope="session")
def get_user_by_field():
    async def _get_user_by_field(field, value):
        async with async_session_maker() as session:
            filter_condition = getattr(User, field) == value
            result = await session.execute(select(User).filter(filter_condition))
            return result.scalar_one_or_none()
    return _get_user_by_field
