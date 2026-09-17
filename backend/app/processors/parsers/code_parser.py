from app.models.document import Document


class CodeParser:

    SUPPORTED_EXTENSIONS = {
        ".py",
        ".js",
        ".ts",
        ".tsx",
        ".jsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
    }

    def parse(self, document: Document) -> str:

        if document.extension.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported source code type: "
                f"{document.extension}"
            )

        return document.content.strip()