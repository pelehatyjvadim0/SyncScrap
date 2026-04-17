import logging

from fastapi import FastAPI

from root.apps.api.v1.router import router as scrap_router
from root.shared.rabbitmq import broker

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    yield
    await broker.stop()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

app = FastAPI(lifespan=lifespan)
app.include_router(scrap_router, prefix="/api/v1")
