from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.models.listing_version import ListingVersion
from root.persistence.relational_store import sessionmaker
from root.shared.observability import metrics

from .schemas import ListListingsInput

__all__ = ["list_listings_tool", "ListListingsInput"]


async def _fetch_listings(
    session: AsyncSession,
    *,
    city: str | None,
    limit: int,
    offset: int,
) -> list[dict[str, Any]]:
    filters = []
    if city:
        filters.append(ListingVersion.city == city)
    stmt = (
        select(ListingVersion)
        .order_by(desc(ListingVersion.created_at))
        .limit(limit)
        .offset(offset)
    )
    if filters:
        stmt = stmt.where(and_(*filters))
    rows = (await session.execute(stmt)).scalars().all()
    out: list[dict[str, Any]] = []
    for row in rows:
        out.append(
            {
                "listing_id": row.idempotency_key,
                "version": row.version,
                "title": row.title,
                "price": float(row.price) if row.price is not None else None,
                "currency": row.currency,
                "city": row.city,
                "url": row.attributes.get("url"),
                "content_hash": row.content_hash,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
        )
    return out


async def list_listings_tool(
    *,
    city: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    with metrics.timer("mcp.db.list_listings.latency_ms"):
        metrics.inc("mcp.db.list_listings.calls")
        try:
            async with sessionmaker() as session:
                items = await _fetch_listings(session, city=city, limit=limit, offset=offset)
        except Exception:
            metrics.inc("mcp.db.list_listings.fail")
            raise
        metrics.inc("mcp.db.list_listings.success")
        return {"ok": True, "items": items, "count": len(items)}
