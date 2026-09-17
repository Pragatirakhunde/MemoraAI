from app.models.document import Document


class TextParser:

    SUPPORTED_EXTENSIONS = {
        ".md",
        ".txt",
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".json",
        ".yaml",
        ".yml",
    }

    def parse(self, document: Document) -> str:

        if document.extension.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported document type: {document.extension}"
            )

        return document.content