from dataclasses import dataclass
from datetime import datetime
from typing import Optional


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


@dataclass
class IndexingServiceConfig:
    """Конфигурация сервиса индексации."""
    chunk_size: int
    batch_size: int
    num_workers: int
    top_k: int

    default_collection: str

@dataclass
class FastAPIConfig:
    host: str
    port: int
    debug: bool

    tmp_dir: str


@dataclass
class ModelsConfig:
    embedding: str


@dataclass
class IndexingStats:
    """Статистика индексации."""
    total_files_processed: int
    successful_files: int
    failed_files: int
    total_chunks_created: int
    processing_time: float
    start_time: datetime
    end_time: Optional[datetime]

