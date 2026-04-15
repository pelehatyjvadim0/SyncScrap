# Стабильный короткий ключ для Redis/HTML-кеша по URL (без зависимости от старого downloader).

import hashlib
from typing import Any
import json
import hashlib

async def url_hash(url: str) -> str:
    return hashlib.blake2b(url.encode(), digest_size=8).hexdigest()

def generate_task_id(prefix: str, data: dict[str, Any]) -> str:
    
    # Универсальный генератор ID для задач.
    # Сортируем ключи, чтобы порядок в словаре не менял хэш.
    # Сериализуем только важные поля в строго определенном порядке
    # или просто дампим отсортированный JSON
    
    canonical_json = json.dumps(data, sort_keys=True, ensure_ascii=False)
    digest = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"