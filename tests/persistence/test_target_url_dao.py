from sqlalchemy.dialects import postgresql

from root.persistence.dao.target_url import TargetUrlDAO
from root.persistence.models.target import TargetUrl


def test_fetch_due_urls_generates_postgres_sql() -> None:
    from datetime import datetime
    from sqlalchemy import select

    stmt = (
        select(TargetUrl.url)
        .where(TargetUrl.is_active.is_(True))
        .where(
            (TargetUrl.last_scraped_at.is_(None)) | (TargetUrl.last_scraped_at < datetime(2020, 1, 1))
        )
        .limit(10)
    )
    compiled = str(stmt.compile(dialect=postgresql.dialect()))
    assert "target_urls" in compiled
    assert "last_scraped_at" in compiled
