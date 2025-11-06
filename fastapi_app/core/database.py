import contextlib
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine, AsyncEngine,
)
from sqlalchemy.orm import declarative_base
from fastapi_app.core.config import config

Base = declarative_base()

class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs: dict[str, Any] = {}):
        self._engine: AsyncEngine | None = create_async_engine(host, **engine_kwargs)
        self._sessionmaker: async_sessionmaker | None = async_sessionmaker(autocommit=False, bind=self._engine, expire_on_commit=False)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(config.DATABASE_URL)
async def get_db_session():
    async with sessionmanager.session() as session:
        yield session

# nu este apelata de nimeni
# a fost apelata in trecut o singura data
async def create_tables():
    async with sessionmanager._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)