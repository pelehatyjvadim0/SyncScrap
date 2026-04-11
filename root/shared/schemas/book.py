from decimal import Decimal
from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, HttpUrl


def _coerce_book_price(v: Any) -> float:
   
    if isinstance(v, bool):
        raise ValueError("price must be numeric")
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, Decimal):
        return float(v)
    if isinstance(v, str):
        return float(v.strip())
    raise TypeError(f"unsupported price type: {type(v)}")


class SBookBase(BaseModel):
    title: str
    price: Annotated[float, BeforeValidator(_coerce_book_price)]
    currency: str
    url: HttpUrl
