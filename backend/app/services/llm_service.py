import time

from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings


class LLMService:

    def __init__(self):

        if not settings.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is not configured."
            )

        self.model = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite",
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
                response = self.model.invoke(prompt)

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