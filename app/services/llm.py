import anthropic
from app.exceptions import SummarizationError
from app.schemas import ArticleSummary
from pydantic import ValidationError
import app.config as config
import logging

logger = logging.getLogger(__name__)


def summarize_article(text: str) -> ArticleSummary:
    """
    Devuelve un ArticleSummary validado a partir del texto.
    Lanza SummarizationError si la llamada al LLM falla
    o si la salida no se puede validar tras un reintento.
    """

    input_schema = ArticleSummary.model_json_schema()
    last_error = None

    for _ in range(2):
        try:
            message = config.client.messages.create(
                model=config.model,
                temperature=config.temperature,
                max_tokens=1000,
                system=(
                    "you are a financial news summarizer. answer in spanish, "
                    "neutral tone and no financial advice."
                ),
                tool_choice={"type": "tool",
                             "name": "extract_article_summary"},
                messages=[
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                tools=[
                    {
                        "name": "extract_article_summary",
                        "description": "Extract a summary of the financial"
                        " news article",
                        "input_schema": input_schema
                    }
                ]
            )
        except anthropic.AnthropicError as e:
            logger.exception(f"LLM call failed: {e}")
            raise SummarizationError("Failed to summarize article") from e

        try:
            return ArticleSummary(**message.content[0].input)
        except ValidationError as e:
            last_error = e
            logger.exception(f"Output validation failed: {e}")
            continue

    raise SummarizationError("Failed to summarize article after retry") from last_error
