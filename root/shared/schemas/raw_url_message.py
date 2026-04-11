from pydantic import BaseModel, HttpUrl


class RawUrlMessage(BaseModel):
    url: HttpUrl
    force_refresh: bool = False

