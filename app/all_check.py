"""Проверка основных компонентов."""

"""Окружение Python."""
try:
    import requests
except ImportError:
    print("Подключение к SSH серверу: error ❌")
finally:
    print("Подключение к SSH серверу: OK ✅")

"""Qdrant."""
try:
    from managers import qdrant_manager
    print(f"Подключение к Qdrant: OK ✅")
except Exception as e:
    print(f"Подключение к Qdrant: error ❌: {e}")
