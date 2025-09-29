import yaml
import logging

from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)


@dataclass
class BaseConfig:
    """Базовая конфигурация"""
    logging: dict


@dataclass
class QdrantConfig:
    """Конфигурация Qdrant."""
    host: str
    port: int
    collections: dict


class QdrantManager:
    """Менеджер для работы с Qdrant."""

    def __init__(self, config_path: str = "./configs/quadrant.yaml") -> None:
        self.base_config: BaseConfig
        self.qdrant_config: QdrantConfig
        self.client: QdrantClient
        self.logger: logging.Logger

        self._load_config(config_path)
        self._setup_logger()

        self._create_client()
        self._create_collections()

    def _load_config(self, config_path: str) -> None:
        """Загрузка конфига."""

        with open(config_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

            self.base_config = BaseConfig(**config_data["base"])
            self.qdrant_config = QdrantConfig(**config_data["qdrant"])

    def _setup_logger(self) -> None:
        """Настройка логирования."""

        log_config = self.base_config.logging
        log_params = {
            "encoding": "utf-8",
            "level": getattr(logging, log_config["level"]),
            "format": "[QM] %(asctime)s - %(levelname)s - %(message)s",
        }

        if log_config["log_in_file"]:
            log_params["filename"] = log_config["file"]

        logging.basicConfig(**log_params) # todo переписать на loguru

        for name in ("httpx", "httpcore", "qdrant_client"):
            logging.getLogger(name).setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)

    def _create_client(self) -> None:
        """Подключение к клиенту Qdrant."""
        self.client = QdrantClient(host=self.qdrant_config.host, port=self.qdrant_config.port)

    def _create_collections(self) -> None:
        """Проверка наличия необходимых коллекций и создание их, если их нет."""

        collections = self.client.get_collections()
        current_collections = [col.name for col in collections.collections]

        for collection in self.qdrant_config.collections.values():
            name = collection["name"]

            if name in current_collections:
                self.logger.info(f"Collection '{name}' exists")
            else:
                try:
                    self.client.create_collection(
                        collection_name=name,
                        vectors_config=VectorParams(
                            size=collection["vector_size"],
                            distance=Distance.COSINE,
                        ),
                    )
                except Exception as e:
                    self.logger.error(f"Error while creating collection: {e}", exc_info=True)
                    raise

                self.logger.info(f"Collection '{name}' created")

    def delete_collection(self, name) -> None:
        """Удаление коллекции."""

        try:
            self.client.delete_collection(name)
            self.logger.info(f"Collection '{name}' deleted")

        except Exception as e:
            self.logger.error(f"Error while deleting collection: {e}", exc_info=True)
            raise

    def close(self):
        """Закрытие соединения с Qdrant."""

        try:
            self.client.close()
            self.logger.info("Qdrant connection closed")
        except Exception as e:
            self.logger.error(f"Error while closing Qdrant connection: {e}, exc_info=True")
            raise


# Глобальный экземпляр менеджера Qdrant
qdrant_manager = QdrantManager()
