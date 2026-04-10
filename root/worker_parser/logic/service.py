import json
import logging
from pydantic import ValidationError

from root.worker_parser.logic.coordinator import ParserCoordinator
from root.worker_parser.logic.schemas import (
    DownloadedPageMessage,
    ExtractedDataMessage,
    StorageProtocol,
)
from root.worker_parser.utils import ParserUtils

logger = logging.getLogger(__name__)


class ParserService:
    @staticmethod
    def parse_downloaded_message(raw_msg) -> DownloadedPageMessage:
        raw_payload = raw_msg.body.decode() if hasattr(raw_msg, "body") else raw_msg

        if isinstance(raw_payload, dict):
            payload = raw_payload
        else:
            payload = json.loads(raw_payload)

        return DownloadedPageMessage.model_validate(payload)

    @staticmethod
    async def parse_page(
        message: DownloadedPageMessage,
        storage: StorageProtocol,
        coordinator: ParserCoordinator,
    ) -> ExtractedDataMessage:
        html = await ParserUtils.storage_get_html(storage, message.storage_key)
        parsed_models = await coordinator.run_parser(str(message.url), html)
        return ExtractedDataMessage(url=message.url, items=parsed_models)

    @staticmethod
    def serialize_for_broker(result: ExtractedDataMessage) -> dict:
        return {
            "url": str(result.url),
            "items": [item.model_dump(mode="json") for item in result.items],
        }