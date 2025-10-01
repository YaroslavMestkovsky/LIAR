from dataclasses import dataclass


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
