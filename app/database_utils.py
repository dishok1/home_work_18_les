from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyAccessTokenDatabase
# ИСПРАВЛЕНО: импортируем из правильного пакета для SQLAlchemy
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

# Импорты ваших моделей
from app.user_models import User, AccessToken

from app.db import get_async_session 

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

async def get_access_token_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyAccessTokenDatabase(session, AccessToken)
