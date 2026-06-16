from app.schemas import ArticleSummary, SummarizeRequest
from app.services.llm import summarize_article
from fastapi import APIRouter, HTTPException
from app.exceptions import SummarizationError
router = APIRouter()


@router.post("/summarize")
def summarize(request: SummarizeRequest) -> ArticleSummary:
    try:
        return summarize_article(request.text)
    except SummarizationError:
        raise HTTPException(status_code=502, detail="No se pudo procesar el artículo")