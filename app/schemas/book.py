from pydantic import BaseModel, HttpUrl


class SBookBase(BaseModel):
    title: str
    price: int | float
    currency: str
    url: HttpUrl
