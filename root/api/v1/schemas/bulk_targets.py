from pydantic import BaseModel, Field


class BulkTargetsRequest(BaseModel):
    urls: list[str] = Field(
        ...,
        description="Список URL для добавления в target_urls",
    )


class BulkTargetsResponse(BaseModel):
    total: int = Field(..., description="Сколько URL пришло в теле")
    inserted: int = Field(..., description="Сколько новых строк записано в БД")
    duplicates: int = Field(
        ...,
        description="Сколько позиций не дало новой строки (повтор в запросе или уже в БД)",
    )
