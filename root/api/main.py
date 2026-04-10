import logging

from fastapi import FastAPI

from root.api.v1.router import router as scrap_router
from root.shared.rabbitmq import router as rabbit_broker_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI()
app.include_router(rabbit_broker_router)
app.include_router(scrap_router, prefix="/api/v1")
