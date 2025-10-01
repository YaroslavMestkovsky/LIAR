import yaml
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
)

from src.helpers import get_configs
from src.project_dataclasses import BaseConfig, QdrantConfig


class QdrantManager:
    """Менеджер для работы с Qdrant."""

    def __init__(self, config_path: str = "/configs/quadrant.yaml") -> None:
        self.base_config: BaseConfig
        self.qdrant_config: QdrantConfig
        self.client: QdrantClient
        self.logger: logging.Logger

        self._load_config(config_path)
        self._setup_logger()

        self._create_client()

    def _load_config(self, config_path: str) -> None:
        """Загрузка конфига."""

        self.base_config, self.qdrant_config = get_configs(
            config_path=config_path,
            config_params={
                BaseConfig: ["base"],
                QdrantConfig: ["qdrant"],
            },
        )

    def _setup_logger(self) -> None:
        """Настройка логирования."""

        log_config = self.base_config.logging
        log_params = {
            "encoding": "utf-8",
            "level": getattr(logging, log_config["level"]),
            "format": "[Q.M.] %(asctime)s - %(levelname)s - %(message)s",
        }

        if log_config["log_in_file"]:
            log_params["filename"] = log_config["file"]

        logging.basicConfig(**log_params) # todo переписать на loguru и вынести в отдельный хелпер

        for name in ("httpx", "httpcore", "qdrant_client"):
            logging.getLogger(name).setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)

    def _create_client(self) -> None:
        """Подключение к клиенту Qdrant."""
        self.client = QdrantClient(host=self.qdrant_config.host, port=self.qdrant_config.port)

    def create_collections(self) -> None:
        """Проверка наличия необходимых коллекций и создание их, если их нет."""

        collections = self.client.get_collections()
        current_collections = [col.name for col in collections.collections]

        for collection in self.qdrant_config.collections.values():
            name = collection["name"]

            if name in current_collections:
                self.logger.debug(f"Коллекция '{name}' уже существует")
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
                    self.logger.error(f"Ошибка при создании коллекции: {e}", exc_info=True)
                    raise

                self.logger.debug(f"Коллекция '{name}' создана")

    def delete_collection(self, name) -> None:
        """Удаление коллекции."""

        try:
            self.client.delete_collection(name)
            self.logger.debug(f"Коллекция '{name}' удалена")

        except Exception as e:
            self.logger.error(f"Ошибка при удалении коллекции: {e}", exc_info=True)
            raise

    def close(self):
        """Закрытие соединения с Qdrant."""

        try:
            self.client.close()
            self.logger.debug("Соединение Qdrant закрыто")
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии соединения с Qdrant: {e}", exc_info=True)
            raise


# Глобальный экземпляр менеджера Qdrant
qdrant_manager = QdrantManager()
