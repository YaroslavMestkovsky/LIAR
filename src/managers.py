from typing import List, Optional, Dict, Any

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    FieldCondition,
    MatchValue,
    Filter,
)

from src.helpers import get_configs
from src.project_dataclasses import BaseConfig, QdrantConfig, SearchResult
from src.web.enums import FileType


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
                QdrantConfig: ["qdrant", "defaults"],
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

    def search_similar(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: float = 0.7,
        file_types: Optional[List[FileType]] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Поиск похожих документов.

        Args:
            query_embedding: Вектор запроса
            limit: Максимальное количество результатов
            score_threshold: Порог схожести
            file_types: Фильтр по типам файлов
            metadata_filter: Фильтр по метаданным

        Returns:
            Список результатов поиска
        """

        try:
            # Построение фильтра
            filter_conditions = []

            if file_types:
                file_type_values = [ft.value for ft in file_types]

                for file_type_value in file_type_values:
                    filter_conditions.append(
                        FieldCondition(
                            key="file_type",
                            match=MatchValue(value=file_type_value),
                        ),
                )

            if metadata_filter:
                for key, value in metadata_filter.items():
                    filter_conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value),
                        ),
                    )

            # Выполнение поиска
            search_filter = Filter(should=filter_conditions) if filter_conditions else None

            search_results = self.client.search(
                collection_name=self.qdrant_config.default_collection,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=search_filter,
            )

            # Преобразование результатов
            results = []

            for result in search_results:
                if result.score >= score_threshold:
                    # Собираем +- 10 результатов от полученного.
                    chunk_index = result.payload.get('chunk_index')
                    chunk_filter = Filter(
                        must=[
                            {
                                "key": "chunk_index",  # путь к полю в payload
                                "range": {
                                    "gte": chunk_index - self.qdrant_config.shift,
                                    "lte": chunk_index + self.qdrant_config.shift,
                                },
                            },
                        ],
                    )

                    points, _ = self.client.scroll(
                        collection_name=self.qdrant_config.default_collection,
                        scroll_filter=chunk_filter,
                        limit=100,
                        with_payload=True,
                    )

                    search_result = SearchResult(
                        ids=[point.id for point in points],
                        chunks=sorted([point.payload.get("chunk_index") for point in points]),
                        file_paths=list(set((point.payload.get("file_path", "") for point in points))),
                        file_types=list(set((FileType(point.payload.get("file_type", "document")) for point in points))),
                        texts=[point.payload.get("text", "") for point in points],
                        score=result.score,
                    )
                    results.append(search_result)

            return results

        except Exception as e:
            self.logger.error(f"Ошибка при поиске: {e}", exc_info=True)
            return []

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
