"""Обратная совместимость: rerank перенесён в `root.persistence.services.rerank`."""

from root.persistence.services.rerank import CrossEncoderReranker

__all__ = ["CrossEncoderReranker"]
