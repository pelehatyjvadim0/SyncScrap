from fastapi import FastAPI
from app.core.rabbitmq import router as rabbit_broker_router
from app.api.v1.router import router as scrap_router
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Вывод в консоль (stdout)
    ],
)
app = FastAPI()
app.include_router(rabbit_broker_router)
app.include_router(scrap_router, prefix="/api/v1")
