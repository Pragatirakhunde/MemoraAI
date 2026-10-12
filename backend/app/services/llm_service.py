import time

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


DEFAULT_ANSWER_FORMATTING = """You are Memora AI. These response-presentation rules apply to EVERY answer by default;
do not wait for the user to ask for formatting.

Write clean, professional, easy-to-scan Markdown while preserving factual accuracy.
- Start with the direct answer, not with a meta statement about how you will format it.
- For a simple question, use one concise paragraph or a short list; do not add unnecessary headings.
- For an explanation with multiple topics, use meaningful Markdown headings and short sections.
- Use bullets for related points and numbered lists for ordered steps or procedures.
- Use **bold** sparingly for important terms or conclusions.
- Format file paths, commands, API routes, identifiers, and short code as inline code.
- Put multi-line code or commands in fenced code blocks with an appropriate language label.
- Use Markdown tables only when comparing structured items or presenting genuinely tabular data.
- Keep paragraphs short. Avoid repeated conclusions, decorative ASCII boxes, empty headings, and unnecessary filler.
- Do not output raw HTML. Do not create citations, file paths, numeric values, or source references that were not provided or retrieved.
- When the evidence is incomplete, state what is known and what cannot be confirmed.
- Follow an explicit user-requested format when it is compatible with accuracy and safety.

Formatting is a default behavior, not an instruction that depends on the user's wording.
"""


class LLMService:

    def __init__(self):

        if not settings.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not configured."
            )

        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.5-flash-lite",
            max_retries=2,
            google_api_key=settings.GOOGLE_API_KEY,
        )


    def generate(
        self,
        prompt: str,
        max_attempts: int = 4,
    ) -> str:

        last_error = None

        for attempt in range(max_attempts):

            try:
                response = self.model.invoke(
                    [
                        SystemMessage(content=DEFAULT_ANSWER_FORMATTING),
                        HumanMessage(content=prompt),
                    ]
                )

                content = response.content

                if isinstance(content, str):
                    return content.strip()

                if isinstance(content, list):

                    text_parts = []

                    for block in content:

                        if isinstance(block, dict):

                            if block.get("type") == "text":
                                text_parts.append(
                                    block.get("text", "")
                                )

                        else:

                            text = getattr(
                                block,
                                "text",
                                None,
                            )

                            if text:
                                text_parts.append(text)

                    return "\n".join(
                        text_parts
                    ).strip()

                return str(content).strip()

            except Exception as exc:

                last_error = exc

                error_text = str(exc)

                is_retryable = (
                    "503" in error_text
                    or "UNAVAILABLE" in error_text
                )

                if not is_retryable:
                    raise

                if attempt == max_attempts - 1:
                    raise

                wait_time = min(
                    5 * (2 ** attempt),
                    30,
                )

                print(
                    f"Gemini temporary error. "
                    f"Retrying in {wait_time}s "
                    f"(attempt {attempt + 1}/{max_attempts})..."
                )

                time.sleep(wait_time)

        raise last_error