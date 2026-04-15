# Имена очередей RabbitMQ для MAS-пайплайна. Контракт: один этап - одна очередь, durable.

from faststream.rabbit import RabbitQueue

DISCOVERY_URLS = RabbitQueue(name="discovery_urls", durable=True)
DISCOVERED_ITEMS = RabbitQueue(name="discovered_items", durable=True)
DELTA_CANDIDATES = RabbitQueue(name="delta_candidates", durable=True)
EXTRACTION_URLS = RabbitQueue(name="extraction_urls", durable=True)
NORMALIZED_ITEMS = RabbitQueue(name="normalized_items", durable=True)
EMBEDDING_TASKS = RabbitQueue(name="embedding_tasks", durable=True)
ENRICHMENT_TASKS = RabbitQueue(name="enrichment_tasks", durable=True)
DEAD_LETTER = RabbitQueue(name="dead_letter", durable=True)
