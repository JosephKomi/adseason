from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(
    settings.async_database_url,
    echo=settings.ENVIRONMENT == "development",
)


@event.listens_for(engine.sync_engine, "connect")
def register_uuid_codec(dbapi_conn, conn_record):
    dbapi_conn.await_(
        dbapi_conn._connection.set_type_codec(
            "uuid",
            encoder=str,
            decoder=str,
            schema="pg_catalog",
            format="text",
        )
    )

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
