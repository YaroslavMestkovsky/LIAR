from typing import List, Dict, Any, Optional
from pydantic import BaseModel


# Pydantic модели для API
class SearchRequest(BaseModel):
    query: str
    file_types: Optional[List[str]] = None
    limit: int = 5
    score_threshold: float = 0.0


class SearchResponseModel(BaseModel):
    query: str
    results: List[Dict[str, Any]]
    total_found: int
    processing_time: float


class IndexingRequest(BaseModel):
    path: str
    file_type: str  # "documents" or "media"
    num_workers: Optional[int] = None


class IndexingResponse(BaseModel):
    success: bool
    message: str
    stats: Optional[Dict[str, Any]] = None
