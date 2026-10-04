import os
from sqlalchemy.orm import declarative_base
from typing import AsyncIterator
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings

Base = declarative_base()

_engine = None

def get_engine() -> AsyncEngine:
  global _engine
  if _engine is None:
    _engine = create_async_engine(settings.DATABASE_URL)
  return _engine

async def get_db_session() -> AsyncIterator[AsyncSession]:
  session_factory = async_sessionmaker(bind=get_engine(), expire_on_commit=False)
  session = session_factory()
  try:
    yield session
    await session.commit()
  except Exception:
    await session.rollback()
    raise
  finally:
    await session.close()