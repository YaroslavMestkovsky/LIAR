import uvicorn

from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from src.all_check import all_check
from src.helpers import get_configs
from src.project_dataclasses import FastAPIConfig
from src.services import IndexingService, QueryService
from src.web.enums import FileType
from src.web.models import SearchResponseModel, SearchRequest, AskResponse, AskRequest

config, = get_configs(
        config_path="/configs/fast_api.yaml",
        config_params={
            FastAPIConfig: ["web", "paths"],
        },
    )


# Инициализация сервисов
indexing_service = IndexingService()
query_service = QueryService()


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


@app.post("/upload")
async def upload_doc(file: UploadFile = File(...)):
    """Загрузка и индексация файла."""

    try:
        # Создание временного файла
        temp_dir = Path(config.tmp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_file = temp_dir / file.filename

        # Сохранение файла
        with open(temp_file, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Индексация файла
        success = indexing_service.index_file(temp_file)

        # Удаление временного файла
        temp_file.unlink()

        if success:
            return {"message": f"Файл {file.filename} успешно проиндексирован"}
        else:
            raise HTTPException(status_code=400, detail="Ошибка при индексации файла")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponseModel)
async def search_api(request: SearchRequest):
    """API для поиска."""
    try:
        # Преобразование типов файлов
        file_types = None

        if request.file_types:
            file_types = [FileType(ft) for ft in request.file_types if ft in [t.value for t in FileType]]

        # Выполнение поиска
        response = query_service.search(
            query=request.query,
            file_types=file_types,
            limit=request.limit,
            score_threshold=request.score_threshold,
        )

        # Преобразование результатов
        results = []
        for result in response.results:
            results.append({
                "ids": result.ids,
                "chunks": result.chunks,
                "file_paths": result.file_paths,
                "file_types": [file_type.value for file_type in result.file_types],
                "texts": result.texts,
                "score": result.score,
            })

        return SearchResponseModel(
            query=response.query,
            results=results,
            total_found=response.total_found,
            processing_time=response.processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest):
    """API для получение ответа из LLM."""





if __name__ == "__main__":
    uvicorn.run(
        "src.web.app:app",
        host=config.host,
        port=config.port,
        reload=config.debug
    )
