from functools import lru_cache
from sentence_transformers import SentenceTransformer

from src.helpers import get_configs
from src.project_dataclasses import ModelsConfig


config, = get_configs(
    config_path="/configs/models.yaml",
    config_params={
        ModelsConfig: ["models"],
    },
)


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Возвращает единственный экземпляр модели эмбеддингов (singleton)."""

    model_name = config.embedding
    model = SentenceTransformer(model_name)

    return model
