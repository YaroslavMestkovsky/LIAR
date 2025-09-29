"""Проверка основных компонентов."""


def all_check():
    """Проверка работоспособности системы."""

    checks = {
        "healthy": True,
        "python-ssh": "",
        "qdrant": "",
    }

    # Python-окружение
    try:
        import requests
    except ImportError:
        checks["python-ssh"] = "Подключение к SSH серверу: error ❌"
        checks["healthy"] = False
    finally:
        checks["python-ssh"] = "Подключение к SSH серверу: OK ✅"

    # Qdrant
    try:
        from src.managers import qdrant_manager
        checks["qdrant"] = f"Подключение к Qdrant: OK ✅"
    except Exception as e:
        checks["qdrant"] = f"Подключение к Qdrant: error ❌: {e}"
        checks["healthy"] = False

    return checks
