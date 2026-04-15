import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from python_ghost_cursor.playwright_async import create_cursor
import random

class HumanActions:
    def __init__(self, page):
        self.page = page
        self.cursor = None

    async def init_cursor(self):
        self.cursor = create_cursor(self.page)
        await self._draw_mouse()

    async def _draw_mouse(self):
        """Внедряет JS для отрисовки красного курсора"""
        await self.page.evaluate('''() => {
            // Создаем элемент для курсора
            const existing = document.getElementById('playwright-cursor-visual');
            if (existing) return; 
            const box = document.createElement('div');
            box.id = 'playwright-cursor-visual';
            box.style.position = 'fixed';
            box.style.top = '0';
            box.style.left = '0';
            box.style.width = '20px';
            box.style.height = '20px';
            box.style.backgroundColor = 'rgba(255, 0, 0, 0.6)'; // Полупрозрачный красный
            box.style.borderRadius = '50%';
            box.style.pointerEvents = 'none'; // Чтобы курсор не мешал кликам
            box.style.zIndex = '9999999'; // Поверх всего
            box.style.transition = 'all 0.1s ease'; // Небольшая плавность для красоты
            document.body.appendChild(box);
            
            // Слушаем движение мыши и двигаем кружок
            document.addEventListener('mousemove', (e) => {
                box.style.left = `${e.pageX - 10}px`; // Центрируем
                box.style.top = `${e.pageY - 10}px`;
            });
        }''')
    
    async def sleep(self, min_seconds=0.5, max_seconds=1.5):
        delay = random.uniform(min_seconds, max_seconds) / 1000
        await asyncio.sleep(delay)
    
    async def smart_scroll(self, selector = None, max_attempts=10):
        if selector is None:
            for _ in range(random.randint(2, 4)):
                await self.page.mouse.wheel(0, random.randint(300, 600))
                await self.sleep()
                await self._draw_mouse()
            await self.page.mouse.wheel(0, random.randint(-600, -300))
            return
            
        for _ in range(max_attempts):
            if await self.page.locator(selector).is_visible():
                print(f"Вижу цель: {selector}")
                break
            
            await self.page.mouse.wheel(0, random.randint(400, 700))
            await self.sleep(500, 800)


    async def human_click(self, selector):
        element = self.page.locator(selector).first
        await element.scroll_into_view_if_needed()

        await self.page.evaluate("window.scrollBy(0, -200)")
        await self.sleep(300, 600)

        await self.cursor.click(element)
        await self.sleep(random.uniform(500, 1000))
    
    async def extract_data(self, card_selector):
        print(f"🔍 Начинаю быстрый сбор данных по селектору: {card_selector}")
        
        # 1. Ждем, пока хотя бы одна карточка появится в DOM
        try:
            await self.page.wait_for_selector(card_selector, timeout=5000)
        except:
            print("⚠️ Карточки не появились вовремя")
            return []

        # 2. Выполняем JS и получаем готовый список словарей
        data = await self.page.evaluate('''
            (selector) => {
                return Array.from(document.querySelectorAll(selector)).map(card => {
                    const titleEl = card.querySelector('a.title');
                    const priceEl = card.querySelector('.price, h4.price');
                    return {
                        title: titleEl?.getAttribute('title') || titleEl?.innerText?.trim() || 'N/A',
                        price: priceEl?.innerText?.trim() || 'N/A',
                        link: titleEl?.href || 'N/A'
                    };
                });
            }
        ''', card_selector)
        
        return data

async def main():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await browser.new_page()

        actions = HumanActions(page)
        await actions.init_cursor()

        print('Заходим на сайт...')
        await page.goto('https://webscraper.io/test-sites/e-commerce/allinone')
        await actions._draw_mouse()

        await actions.human_click('text="Accept"')
        await actions._draw_mouse()
        await actions.sleep(1000, 2000)
        await actions.smart_scroll()

        print('Перехожу в категории!')
        await actions.human_click('text="Computers"')
        await actions._draw_mouse()
        await actions.sleep(1000, 3000)
        await actions.smart_scroll()

        await actions.human_click('text="Laptops"')
        await actions._draw_mouse()
        await actions.sleep(1000, 2000)
        
        print('Парсим данные...')
        data = await actions.extract_data('.thumbnail')
        
        import json
        print(f"✅ Успешно собрано товаров: {len(data)}")
        print(json.dumps(data[:3], indent=4, ensure_ascii=False))


if __name__ == '__main__':
    asyncio.run(main())
        