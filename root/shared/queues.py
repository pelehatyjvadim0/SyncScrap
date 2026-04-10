from faststream.rabbit import RabbitQueue

RAW_URLS = RabbitQueue(name="raw_urls", durable=True)
DOWNLOADED_PAGES = RabbitQueue(name="downloaded_pages", durable=True)
EXTRACTED_DATA = RabbitQueue(name="extracted_data", durable=True)
