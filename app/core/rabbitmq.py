from faststream.rabbit.fastapi import RabbitRouter
from faststream.rabbit import RabbitBroker, Channel
from faststream import FastStream
from app.core.config import settings

router = RabbitRouter(
    settings.rabbit.RABBITMQ_URL, setup_state=Channel(prefetch_count=1)
)

broker: RabbitBroker = router.broker

faststream_app = FastStream(broker)
