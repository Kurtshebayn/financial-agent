from types import SimpleNamespace
import anthropic
from app import config
from app.exceptions import SummarizationError
from app.services.llm import summarize_article
from app.schemas import ArticleSummary
import pytest


def test_summarize_article_happy_path(monkeypatch):
    fake_input = {
        "is_financial_news": True,
        "summary": "Resumen de prueba.",
        "key_points": ["punto uno", "punto dos"],
        "assets_mentioned": [],
        "overall_sentiment": "neutral",
    }
    fake_block = SimpleNamespace(input=fake_input)
    fake_message = SimpleNamespace(content=[fake_block])

    monkeypatch.setattr(config.client.messages, "create",
                        lambda **kwargs: fake_message)

    result = summarize_article("un texto largo, mayor a cincuenta caracteres, para pasar la validacion")

    assert isinstance(result, ArticleSummary)
    assert result.is_financial_news is True
    assert result.overall_sentiment.value == "neutral"


def test_summarize_article_summarization_error(monkeypatch):
    def boom(**kwargs):
        raise anthropic.AnthropicError("falla simulada")
    monkeypatch.setattr(config.client.messages, "create", boom)

    with pytest.raises(SummarizationError):
        summarize_article("un texto largo, mayor a cincuenta caracteres, para pasar la validacion")


def test_summarize_article_retry(monkeypatch):
    call_count = {"count": 0}
    fake_input = {
                "is_financial_news": True,
                "summary": "Resumen de prueba.",
                "key_points": ["punto uno", "punto dos"],
                "assets_mentioned": [],
                "overall_sentiment": "neutral",
            }

    def fake_create(**kwargs):
        call_count["count"] += 1
        if call_count["count"] == 1:
            bad_input = {**fake_input, "overall_sentiment": "super_bullish"}
            return SimpleNamespace(content=[SimpleNamespace(input=bad_input)])
        return SimpleNamespace(content=[SimpleNamespace(input=fake_input)])

    monkeypatch.setattr(config.client.messages, "create", fake_create)

    result = summarize_article("un texto largo, mayor a cincuenta caracteres, para pasar la validacion")

    assert isinstance(result, ArticleSummary)
    assert call_count["count"] == 2
    assert result.is_financial_news is True
    assert result.overall_sentiment.value == "neutral"
