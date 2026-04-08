from core.database import sessionmaker
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

class DependsGenerator:
    @staticmethod
    async def get_db():
        async with sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                
SessionDep = Annotated[AsyncSession, Depends(DependsGenerator.get_db)]