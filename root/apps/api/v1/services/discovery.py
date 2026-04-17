from root.shared.url_spawner import URLSpawner


class DiscoveryService:
    @staticmethod
    async def enqueue(
        *,
        search_urls: list[str],
        source: str,
        city: str | None,
        category: str | None,
    ) -> list[str]:
        return await URLSpawner.append_discovery_tasks(
            search_urls,
            source=source,
            city=city,
            category=category,
        )
