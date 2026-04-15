from faststream.rabbit import RabbitQueue

# Legacy queues
RAW_URLS = RabbitQueue(name="raw_urls", durable=True)
RAW_URLS_PLAYWRIGHT = RabbitQueue(name="raw_urls_playwright", durable=True)
DOWNLOADED_PAGES = RabbitQueue(name="downloaded_pages", durable=True)
EXTRACTED_DATA = RabbitQueue(name="extracted_data", durable=True)

# Multi-stage MVP queues
DISCOVERY_URLS = RabbitQueue(name="discovery_urls", durable=True)
DISCOVERED_ITEMS = RabbitQueue(name="discovered_items", durable=True)
DELTA_CANDIDATES = RabbitQueue(name="delta_candidates", durable=True)
EXTRACTION_URLS = RabbitQueue(name="extraction_urls", durable=True)
NORMALIZED_ITEMS = RabbitQueue(name="normalized_items", durable=True)
EMBEDDING_TASKS = RabbitQueue(name="embedding_tasks", durable=True)
ENRICHMENT_TASKS = RabbitQueue(name="enrichment_tasks", durable=True)
DEAD_LETTER = RabbitQueue(name="dead_letter", durable=True)
