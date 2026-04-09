from pathlib import Path
import json
import aiofiles
from app.core.rabbitmq import broker
from app.core.queues import URLS_QUEUE
import logging

logger = logging.getLogger(__name__)


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class URLSpawner:
    @classmethod
    async def _get_urls_dict(cls) -> dict:
        try:
            async with aiofiles.open(BASE_DIR / "url.json", "r", encoding="utf-8") as f:
                content = await f.read()

            tasks_url = json.loads(content).get("tasks")

            if not tasks_url:
                raise ValueError()
            return tasks_url
        except Exception:
            logger.critical(' [!] Произошла критическая ошибка чтения файла "url.json"')
            raise ValueError(
                "Ошибка json файла с URL, проверьте его наличие и структуру!"
            )

    @classmethod
    async def append_urls_in_queue(cls, list_urls: list):

        logger.info(" [*] Начинаю заполнение очереди URL")
        
        complete_url_counter = 0
        
        if list_urls:
            for url in list_urls:

                try:
                    await broker.publish(message=url, queue=URLS_QUEUE)
                    complete_url_counter += 1
                    logger.info(f" [+] Сообщение {complete_url_counter} улетело в RabbitMQ")
                except Exception as e:
                    logger.error(
                        f" [!] Произошла ошибка добавления URL в очередь URLS_QUEUE, пропускаю.\nТекст ошибки: {e}"
                    )
                    continue

            logger.info(
                f" [v] Добавление URL в очередь URLS_QUEUE завершено!\nВсего URL: {len(list_urls)} | Успешно: {complete_url_counter}"
            )
