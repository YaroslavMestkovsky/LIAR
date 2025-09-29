import uvicorn

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

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

# Инициализация сервисов
# config = get_config() todo
# indexing_service = IndexingService()
# query_service = QueryService()

# Настройка статических файлов и шаблонов
static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

if static_dir.exists():
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

if templates_dir.exists():
    templates = Jinja2Templates(directory=templates_dir)
else:
    templates = None


if __name__ == "__main__":
    config = get_config()

    uvicorn.run(
        "src.web.app:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
