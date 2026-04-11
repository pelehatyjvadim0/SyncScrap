from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from root.shared.config import settings

engine = create_async_engine(url=settings.db.DATABASE_URL)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)
