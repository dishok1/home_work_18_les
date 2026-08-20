import os
import sys
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

current_script_path = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_script_path, '..', 'database.env')

load_dotenv(dotenv_path)


class TestSettings():
    DB_HOST_TEST: str = os.environ.get("DB_HOST_TEST") or "127.0.0.1"
    DB_PORT_TEST: str = os.environ.get("DB_PORT_TEST") or "5432"
    DB_NAME_TEST: str = os.environ.get("DB_NAME_TEST") or "test_db"
    DB_USER_TEST: str = os.environ.get("DB_USER_TEST") or "postgres"
    DB_PASS_TEST: str = os.environ.get("DB_PASS_TEST") or "123321"
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"


class ProdSettings():
    DB_HOST: str = os.environ.get("DB_HOST") or "127.0.0.1"
    DB_PORT: str = os.environ.get("DB_PORT") or "5432"
    DB_NAME: str = os.environ.get("DB_NAME") or "fastapi_test"
    DB_USER: str = os.environ.get("DB_USER") or "postgres"
    DB_PASS: str = os.environ.get("DB_PASS") or "123321"
    DATABASE_URL: str = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

def get_settings():
    env = os.getenv("ENVIRONMENT", "production")
    if env is None:
        raise ValueError("ENVIRONMENT variable is not set!")
    env = env.lower()
    if env == "testing":
        return TestSettings()
    elif env == "production":
        return ProdSettings()
    else:
        raise ValueError(f"Unknown environment: {env}!")


settings = get_settings()
