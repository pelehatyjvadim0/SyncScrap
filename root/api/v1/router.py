from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from root.api.v1.schemas import BulkTargetsRequest, BulkTargetsResponse
from root.api.v1.services import BulkTargetsService, InvalidTargetUrlError
from root.shared.dependencies import DependsGenerator

from root.persistence.dao.listing import ListingDAO
from root.shared.schemas. listing import ListingRecord

from datetime import datetime, timezone

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

# костыль для теста. Позже переделать и рассортировать логику между сервисом и DAO
@router.get('/testing_get_items/{limit:int}',
            summary='Выгрузка данных по лимиту')
async def testing_get_items(limit: int = 10, session: AsyncSession = Depends(DependsGenerator.get_db)):
    if limit > 500:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Доступно не более 500 позиций к выгрузке!')
    try:
        results = await ListingDAO.get_listing(session, limit)
        now_utc = datetime.now(timezone.utc)
        formatted_date = now_utc.strftime("%Y %m %d %H:%M:%S")

        data = {
            'hi_message': 'Привет от Вадима!',
            'count_items': len(results),
            'upload_time': formatted_date,
            'items': []
        }

        for res in results:
            res_val = ListingRecord.model_validate(res)
            data['items'].append(res_val.model_dump())
        
        return {'status': 'ok', 'payload': data}
    
    except Exception as e:
        print(e)
        raise HTTPException(detail='Ошибка со стороны сервера', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)