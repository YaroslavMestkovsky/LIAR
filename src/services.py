import logging

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List

from src.helpers import get_configs
from src.managers import qdrant_manager, QdrantManager
from src.processors import DocumentProcessor
from src.project_dataclasses import IndexingServiceConfig, BaseConfig, IndexingStats


class IndexingService:
    """Сервис индексации."""

    def __init__(self, config_path: str = "/configs/indexer.yaml"):
        self.config: IndexingServiceConfig
        self.base_config: BaseConfig

        self._load_config(config_path)
        self._setup_logger()

        self.num_workers = self.config.num_workers
        self.qdrant_manager: QdrantManager = qdrant_manager
        self.document_processor: DocumentProcessor = DocumentProcessor(
            self.config.chunk_size,
            self.qdrant_manager.client,
            self.config,
            self.base_config,
        )

        # Статистика
        self.stats = IndexingStats(
            total_files_processed=0,
            successful_files=0,
            failed_files=0,
            total_chunks_created=0,
            processing_time=0.0,
            start_time=datetime.now(),
            end_time=None,
        )

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

    def index_file(self, file_path: Path) -> bool:
        """Индексация одного файла."""

        if not file_path.exists():
            self.logger.error(f"Файл не существует: {file_path}")
            return False

        try:
            suffix = file_path.suffix.lower()

            # Определение типа файла и выбор процессора
            if suffix in self.document_processor.document_formats:
                return self.document_processor.process_file(suffix, file_path)
            else:
                return False
            # elif _MEDIA_AVAILABLE and self.media_processor is not None and suffix in (
            #         self.media_processor.video_formats | self.media_processor.audio_formats | self.media_processor.image_formats
            # ):
            #     return self.media_processor.process_file(file_path)
            # else:
            #     logger.warning(f"Неподдерживаемый формат файла: {suffix}")
            #     return False

        except Exception as e:
            self.logger.error(f"Ошибка при индексации файла {file_path}: {e}", exc_info=True)
            return False

    def index_documents(self, docs_path: Path):
        """Индексация документов."""

        start_time = datetime.now()

        self.logger.debug(f"Начало индексации документов: {docs_path}")
        self.logger.debug(f"Количество воркеров: {self.num_workers}")

        try:
            document_files = self._find_document_files(docs_path)
            self.logger.debug(f"Найдено {len(document_files)} документов для индексации")

            if not document_files:
                self.logger.warning("Документы для индексации не найдены")
                return self._finalize_stats(start_time)

            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                future_to_file = {
                    executor.submit(self._process_document_file, file_path): file_path
                    for file_path in document_files
                }

                with tqdm(total=len(document_files), desc="Индексация документов") as pbar:
                    for future in as_completed(future_to_file):
                        file_path = future_to_file[future]

                        try:
                            success = future.result()

                            if success:
                                self.stats.successful_files += 1
                            else:
                                self.stats.failed_files += 1
                        except Exception as e:
                            self.logger.error(f"Ошибка при обработке документа {file_path}: {e}")
                            self.stats.failed_files += 1

                        self.stats.total_files_processed += 1
                        pbar.update(1)

            # Финализация процессора
            self.document_processor.finalize()

            self.logger.debug(
                f"Индексация документов завершена. Успешно: {self.stats.successful_files}, "
                f"Ошибок: {self.stats.failed_files}",
            )
            return self._finalize_stats(start_time)
        except Exception as e:
            self.logger.error(f"Ошибка при индексации документов: {e}", exc_info=True)
            return self._finalize_stats(start_time)

    def _find_document_files(self, directory: Path) -> List[Path]:
        """Поиск документов в директории."""

        document_files = []
        supported_formats = set(self.document_processor.document_formats.keys())

        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in supported_formats:
                document_files.append(file_path)

        return document_files

    def _process_document_file(self, file_path: Path) -> bool:
        """Обработка одного документа."""

        try:
            return self.document_processor.process_file(file_path)
        except Exception as e:
            self.logger.error(f"Ошибка при обработке документа {file_path}: {e}")
            return False

    def _finalize_stats(self, start_time: datetime) -> IndexingStats:
        """Финализация статистики."""

        self.stats.end_time = datetime.now()
        self.stats.processing_time = (self.stats.end_time - start_time).total_seconds()

        return self.stats
