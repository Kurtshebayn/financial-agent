from enum import Enum
from pydantic import BaseModel, Field


class AssetType(str, Enum):
    equity = "equity"; crypto = "crypto"; commodity = "commodity"
    forex = "forex"; index = "index"; other = "other"


class Sentiment(str, Enum):
    bullish = "bullish"; neutral = "neutral"; bearish = "bearish"


class Asset(BaseModel):
    name: str = Field(description="Nombre o ticker del activo, ej. 'NVDA', 'Bitcoin'")
    asset_type: AssetType


class ArticleSummary(BaseModel):
    is_financial_news: bool = Field(description="False si el texto no es noticia financiera o de mercados")
    summary: str = Field(description="Resumen neutral de 2 a 3 frases")
    key_points: list[str] = Field(description="Hasta 5 hechos concretos del artículo")
    assets_mentioned: list[Asset] = Field(default_factory=list)
    overall_sentiment: Sentiment = Field(description="Tono del artículo hacia los activos, NO consejo de inversión")


class SummarizeRequest(BaseModel):
    text: str = Field(min_length=50)