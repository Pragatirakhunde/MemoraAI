from pathlib import Path

from app.connectors.base import BaseConnector, ConnectorFile


class LocalDirectoryConnector(BaseConnector):

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

    def __init__(self, directory: str):
        self.directory = Path(directory)

    def validate(self) -> bool:
        return self.directory.exists() and self.directory.is_dir()

    def list_files(self) -> list[ConnectorFile]:

        if not self.validate():
            raise ValueError(
                f"Directory does not exist: {self.directory}"
            )

        files = []

        for file_path in self.directory.rglob("*"):

            if not file_path.is_file():
                continue

            if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
                continue

            files.append(
                ConnectorFile(
                    path=str(file_path),
                    name=file_path.name,
                    extension=file_path.suffix.lower(),
                    size=file_path.stat().st_size,
                )
            )

        return files

    def read_file(self, path: str) -> str:

        file_path = Path(path)

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {path}"
            )

        return file_path.read_text(
            encoding="utf-8"
        )