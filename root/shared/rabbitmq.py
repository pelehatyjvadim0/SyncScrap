from faststream.rabbit import RabbitBroker, Channel
from faststream import FastStream
from root.shared.config import settings

broker: RabbitBroker = RabbitBroker(
    settings.rabbit.RABBITMQ_URL,
    default_channel=Channel(prefetch_count=1),
)

faststream_app = FastStream(broker)
