from app.models.document import Document


class PlainTextParser:

    SUPPORTED_EXTENSIONS = {
        ".txt",
        ".json",
        ".yaml",
        ".yml",
    }

    def parse(self, document: Document) -> str:

        if document.extension.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported text type: "
                f"{document.extension}"
            )

        return document.content.strip()