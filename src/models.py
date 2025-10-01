from functools import lru_cache


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Возвращает единственный экземпляр модели эмбеддингов (singleton)."""

    config = get_config()
    model_name = config.models.embedding
    logger.info(f"Загрузка общей модели эмбеддингов: {model_name}")
    model = SentenceTransformer(model_name)
    logger.info("Общая модель эмбеддингов загружена")
    return model


