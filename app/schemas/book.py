from pydantic import BaseModel

class SBookBase(BaseModel):
    title: str
    price: int | float
    currency: str