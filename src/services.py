import logging
from datetime import datetime
from pathlib import Path
from typing import List

import yaml

from src.helpers import get_configs
from src.managers import qdrant_manager, QdrantManager
from src.project_dataclasses import IndexingServiceConfig, BaseConfig


class IndexingService:
    """Сервис индексации."""

    def __init__(self, config_path: str = "/configs/indexer.yaml"):
        self.config: IndexingServiceConfig
        self.base_config: BaseConfig

        self._load_config(config_path)
        self._setup_logger()

        self.qdrant_manager: QdrantManager = qdrant_manager

    def _load_config(self, config_path: str) -> None:
        """Загрузка конфига."""

        self.base_config, self.config = get_configs(
            config_path=config_path,
            config_params={
                BaseConfig: ["base"],
                IndexingServiceConfig: ["processing", "defaults"],
            },
        )

    def _setup_logger(self) -> None:
        """Настройка логирования."""

        log_config = self.base_config.logging
        log_params = {
            "encoding": "utf-8",
            "level": getattr(logging, log_config["level"]),
            "format": "[I.S.] %(asctime)s - %(levelname)s - %(message)s",
        }

        if log_config["log_in_file"]:
            log_params["filename"] = log_config["file"]

        logging.basicConfig(**log_params) # todo переписать на loguru и вынести в отдельный хелпер

        for name in ("httpx", "httpcore", "qdrant_client"):
            logging.getLogger(name).setLevel(logging.WARNING)

        self.logger = logging.getLogger(__name__)

    def index_documents(self, docs_path: Path):
        """Индексация документов."""

        start_time = datetime.now()

        self.logger.info(f"Начало индексации документов: {docs_path}")
        self.logger.info(f"Количество воркеров: {self.config.num_workers}")

    def _find_document_files(self, directory: Path) -> List[Path]:
        """Поиск документов в директории."""

        document_files = []
        supported_formats = set(self.document_processor.document_formats.keys())

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                document_files.append(file_path)

        return document_files
