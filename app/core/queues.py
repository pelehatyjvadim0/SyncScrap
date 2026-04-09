from faststream.rabbit import RabbitQueue

URLS_QUEUE = RabbitQueue(name="urls_to_fetch_n_scrap", durable=True)
DAO_QUEUE = RabbitQueue(name="dict_data", durable=True)
