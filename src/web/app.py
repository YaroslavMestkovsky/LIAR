import uvicorn

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.all_check import all_check
from src.web.helpers import get_config


# Инициализация FastAPI
app = FastAPI(
    title="Local AI Assistant",
    description="Система локальной поддержки ИИ для поиска по документам и медиафайлам",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка статических файлов и шаблонов
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if templates_dir.exists():
    templates = Jinja2Templates(directory=templates_dir)
else:
    templates = None


@app.get("/health")
async def health_check():
    """Проверка состояния системы."""

    checks = all_check()

    return {
        "status": "healthy" if checks.pop("healthy") else "unhealthy",
        **checks,
    }

if __name__ == "__main__":
    config = get_config()

    uvicorn.run(
        "src.web.app:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
