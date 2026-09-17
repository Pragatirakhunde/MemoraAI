import re
import unicodedata


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:

        if not text:
            return ""

        # Normalize line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")

        # Remove UTF-8 BOM
        text = text.replace("\ufeff", "")

        # Remove null characters
        text = text.replace("\x00", "")

        # Normalize Unicode
        text = unicodedata.normalize(
            "NFKC",
            text,
        )

        # Remove trailing spaces only.
        # Keep leading spaces because source-code
        # indentation may be important.
        text = re.sub(
            r"[ \t]+$",
            "",
            text,
            flags=re.MULTILINE,
        )

        # Limit excessive blank lines
        text = re.sub(
            r"\n{4,}",
            "\n\n\n",
            text,
        )

        # Remove blank space at beginning/end
        text = text.strip()

        return text