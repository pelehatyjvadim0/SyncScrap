from app.core.database import sessionmaker
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import httpx


class DependsGenerator:
    @staticmethod
    async def get_db():
        async with sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()

    @staticmethod
    async def get_httpx_client():
        async with httpx.AsyncClient() as client:
            yield client


SessionDep = Annotated[AsyncSession, Depends(DependsGenerator.get_db)]
