from pathlib import Path

from app.models.document import Document


class MetadataExtractor:

    LANGUAGE_MAP = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".tsx": "TypeScript React",
        ".jsx": "JavaScript React",
        ".java": "Java",
        ".cpp": "C++",
        ".c": "C",
        ".h": "C/C++ Header",
        ".json": "JSON",
        ".yaml": "YAML",
        ".yml": "YAML",
        ".md": "Markdown",
        ".txt": "Plain Text",
    }

    DOCUMENT_TYPE_MAP = {
        ".md": "documentation",
        ".txt": "text",
        ".py": "source_code",
        ".js": "source_code",
        ".ts": "source_code",
        ".tsx": "source_code",
        ".jsx": "source_code",
        ".java": "source_code",
        ".cpp": "source_code",
        ".c": "source_code",
        ".h": "source_code",
        ".json": "configuration",
        ".yaml": "configuration",
        ".yml": "configuration",
    }

    @classmethod
    def extract(
        cls,
        document: Document,
        text: str,
    ) -> dict:

        path = Path(document.file_path)

        extension = document.extension.lower()

        return {
            "title": document.title,
            "filename": path.name,
            "extension": extension,
            "language": cls.LANGUAGE_MAP.get(
                extension,
                "Unknown",
            ),
            "document_type": cls.DOCUMENT_TYPE_MAP.get(
                extension,
                "unknown",
            ),
            "file_path": document.file_path,
            "character_count": len(text),
            "line_count": len(text.splitlines()),
            "word_count": len(text.split()),
            "checksum": document.checksum,
        }