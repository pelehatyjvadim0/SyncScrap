import logging

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from root.shared.config import settings

logger = logging.getLogger(__name__)

_engine_kwargs: dict = {
    "pool_pre_ping": settings.db.POOL_PRE_PING,
    "pool_recycle": settings.db.POOL_RECYCLE,
    "pool_size": settings.db.POOL_SIZE,
    "max_overflow": settings.db.MAX_OVERFLOW,
}

engine = create_async_engine(settings.db.DATABASE_URL, **_engine_kwargs)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)

logger.debug(
    " [DB] Async engine: pool_size=%s max_overflow=%s pre_ping=%s recycle=%s",
    settings.db.POOL_SIZE,
    settings.db.MAX_OVERFLOW,
    settings.db.POOL_PRE_PING,
    settings.db.POOL_RECYCLE,
)
