from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, HttpUrl, ConfigDict


def _coerce_price(v: Any) -> float:
    if isinstance(v, bool):
        raise ValueError("price must be numeric")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, str):
        return float(v.strip())
    raise TypeError(f"unsupported price type: {type(v)}")


class ListingRecord(BaseModel):
    """Общая форма записи для сохранения в БД; доменные поля кладём в `extra` в worker_db."""

    title: str
    price: Annotated[float, BeforeValidator(_coerce_price)]
    currency: str
    url: HttpUrl

    model_config = ConfigDict(from_attributes=True)
