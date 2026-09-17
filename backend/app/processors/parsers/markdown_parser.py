import re

from app.models.document import Document


class MarkdownParser:

    def parse(self, document: Document) -> str:
        text = document.content

        # Keep code blocks, headings and normal text.
        # Remove Markdown image syntax.
        text = re.sub(
            r"!\[.*?\]\(.*?\)",
            "",
            text,
        )

        # Convert links to their visible text.
        text = re.sub(
            r"\[([^\]]+)\]\([^)]+\)",
            r"\1",
            text,
        )

        return text.strip()