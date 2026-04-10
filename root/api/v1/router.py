from fastapi import APIRouter
from root.api.v1.scraper_utils import ScraperUtils
from root.api.v1.url_spawner import URLSpawner

router = APIRouter()

@router.post("/start-scrap")
async def start_scrap(limit: int):
    urls_list = await ScraperUtils.get_all_book_urls(limit)
    await URLSpawner.append_urls_in_queue(urls_list)
