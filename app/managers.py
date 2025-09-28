import yaml

from dataclasses import dataclass
from typing import Optional
from qdrant_client import QdrantClient


@dataclass
class QdrantConfig:
    """Конфигурация Qdrant."""
    host: str
    port: int
    collection: str


class QdrantManager:
    """Менеджер для работы с Qdrant."""

    def __init__(self, config_path: str = "/app/configs/quadrant.yaml") -> None:
        self.config: QdrantConfig
        self.client: QdrantClient

        self._load_config(config_path)
        self._create_client()
        self.collection_name = self.config.collection

    def _load_config(self, config_path: str) -> None:
        """Загрузка конфига."""
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)
            self.config = QdrantConfig(**config_data["qdrant"])

    def _create_client(self) -> None:
        """Подключение к клиенту Qdrant."""
        self.client = QdrantClient(host=self.config.host, port=self.config.port)
