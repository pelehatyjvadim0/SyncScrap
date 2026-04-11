from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from root.api.v1.schemas import BulkTargetsRequest, BulkTargetsResponse
from root.api.v1.services import BulkTargetsService, InvalidTargetUrlError
from root.shared.dependencies import DependsGenerator

router = APIRouter()


@router.post(
    "/targets/bulk",
    response_model=BulkTargetsResponse,
    summary="Массовое добавление целей (скрап)",
)
async def add_targets_urls(
    body: BulkTargetsRequest,
    session: AsyncSession = Depends(DependsGenerator.get_db),
) -> BulkTargetsResponse:

    try:
        return await BulkTargetsService.add_urls(session, body.urls)
    except InvalidTargetUrlError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
