# Минимальное сообщение с URL для кеша hunter (force_refresh обходит Redis).
# Legacy-имя сохранено для совместимости с сообщениями брокера.

from pydantic import BaseModel, HttpUrl


class RawUrlMessage(BaseModel):
    url: HttpUrl
    force_refresh: bool = False

