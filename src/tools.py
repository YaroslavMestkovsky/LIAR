from src.managers import qdrant_manager


def create_collections():
    """Создание коллекций Qdrant."""

    qdrant_manager.create_collections()


if __name__ == "__main__":
    create_collections()
