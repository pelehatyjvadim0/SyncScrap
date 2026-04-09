import httpx 
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class ScraperUtils:
    @staticmethod
    async def get_all_book_urls(limit: int = 100):
        base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
        urls = []
        page = 1
        
        async with httpx.AsyncClient() as client:
            while len(urls) < limit:
                response = await client.get(base_url.format(page))
                
                if response.status_code != 200:
                    logger.error(f' [!] Ошибка обращения к ресурсу. Статус: {response.status_code}. Прерываю сбор URL')
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                links = soup.select('h3 a')
                
                for link in links:
                    clear_url = link['href'].replace('../../../', '')
                    full_url = 'https://books.toscrape.com/catalogue/' + clear_url
                    urls.append(full_url)
                    print(full_url)
                    
                    if len(urls) >= limit:
                        break
                
                page +=1
                
        return urls