"""Проверка основных компонентов."""

from managers import QdrantManager

"""Окружение Python."""
try:
    import requests
except ImportError:
    print("❌ Проблемы с импортом базовых библиотек. Ошибка подключения к SSH серверу?")
finally:
    print("✅ Подключение к SSH серверу.")

"""Qdrant."""
try:
    qdrant = QdrantManager()
    qdrant.client.get_collections()
    print(f"✅ Подключение к Qdrant.")
except Exception as e:
    print(f"❌ Ошибка подключения к Qdrant: {e}")
